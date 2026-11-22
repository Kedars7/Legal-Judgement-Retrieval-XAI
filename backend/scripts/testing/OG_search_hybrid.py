import json
import pickle
import re
import textwrap
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2])
)

from ranking.feature_extractor import extract_features


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "law-ai/InLegalBERT"

FAISS_INDEX_PATH = Path(
    "index/baseline_100/legal_judgments.faiss"
)

METADATA_PATH = Path(
    "embeddings/baseline_100/metadata.jsonl"
)

BM25_INDEX_PATH = Path(
    "index/bm25/bm25.pkl"
)

BM25_METADATA_PATH = Path(
    "index/bm25/bm25_metadata.pkl"
)


# Candidate pool from each retriever
DENSE_TOP_K = 50
BM25_TOP_K = 50

# Final hybrid results
HYBRID_TOP_K = 20

# Maximum chunks from the same judgment
MAX_CHUNKS_PER_JUDGMENT = 2

# Reciprocal Rank Fusion constant
RRF_K = 60

# Query maximum tokens
MAX_LENGTH = 512

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    return re.findall(
        r"\b\w+\b",
        text.lower()
    )


# ============================================================
# MEAN POOLING
# ============================================================

def mean_pooling(
    last_hidden_state,
    attention_mask
):

    mask = (
        attention_mask
        .unsqueeze(-1)
        .expand(last_hidden_state.size())
        .float()
    )

    masked_embeddings = (
        last_hidden_state * mask
    )

    summed = torch.sum(
        masked_embeddings,
        dim=1
    )

    counts = torch.clamp(
        mask.sum(dim=1),
        min=1e-9
    )

    return summed / counts


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("Loading InLegalBERT...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    model.to(DEVICE)
    model.eval()

    print("InLegalBERT loaded.")

    return tokenizer, model


# ============================================================
# LOAD FAISS
# ============================================================

def load_faiss():

    print("Loading FAISS index...")

    index = faiss.read_index(
        str(FAISS_INDEX_PATH)
    )

    print(
        f"FAISS vectors: {index.ntotal}"
    )

    return index


# ============================================================
# LOAD CURRENT V1 METADATA
# ============================================================

def load_metadata():

    print("Loading V1 metadata...")

    metadata = []

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():

                metadata.append(
                    json.loads(line)
                )

    print(
        f"Metadata records: {len(metadata)}"
    )

    return metadata


# ============================================================
# LOAD BM25
# ============================================================

def load_bm25():

    print("Loading BM25 index...")

    with open(
        BM25_INDEX_PATH,
        "rb"
    ) as f:

        bm25 = pickle.load(f)

    print("BM25 index loaded.")

    with open(
        BM25_METADATA_PATH,
        "rb"
    ) as f:

        bm25_metadata = pickle.load(f)

    print(
        f"BM25 metadata records: "
        f"{len(bm25_metadata)}"
    )

    if len(bm25_metadata) != len(bm25.doc_freqs):

        raise ValueError(
            "BM25 metadata count does not "
            "match BM25 document count."
        )

    return bm25, bm25_metadata


# ============================================================
# CREATE QUERY EMBEDDING
# ============================================================

def create_query_embedding(
    query,
    tokenizer,
    model
):

    encoded = tokenizer(
        [query],
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )

    encoded = {
        key: value.to(DEVICE)
        for key, value in encoded.items()
    }

    with torch.no_grad():

        output = model(
            **encoded
        )

        embedding = mean_pooling(
            output.last_hidden_state,
            encoded["attention_mask"]
        )

        embedding = torch.nn.functional.normalize(
            embedding,
            p=2,
            dim=1
        )

    return (
        embedding
        .cpu()
        .numpy()
        .astype("float32")
    )


# ============================================================
# DENSE / FAISS SEARCH
# ============================================================

def dense_search(
    query,
    index,
    metadata,
    tokenizer,
    model
):

    query_embedding = create_query_embedding(
        query,
        tokenizer,
        model
    )

    scores, indices = index.search(
        query_embedding,
        DENSE_TOP_K
    )

    results = []

    for rank, (
        score,
        vector_id
    ) in enumerate(
        zip(
            scores[0],
            indices[0]
        ),
        start=1
    ):

        if vector_id < 0:
            continue

        vector_id = int(vector_id)

        if vector_id >= len(metadata):
            continue

        results.append({

            "vector_id": vector_id,

            "dense_score": float(score),

            "dense_rank": rank

        })

    return results


# ============================================================
# BM25 SEARCH
# ============================================================

def bm25_search(
    query,
    bm25,
    metadata
):

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    scores = bm25.get_scores(
        query_tokens
    )

    ranked_indices = (
        np.argsort(scores)[::-1]
        [:BM25_TOP_K]
    )

    results = []

    for rank, index in enumerate(
        ranked_indices,
        start=1
    ):

        index = int(index)

        results.append({

            "vector_id": index,

            "bm25_score": float(
                scores[index]
            ),

            "bm25_rank": rank

        })

    return results


# ============================================================
# VALIDATE MAPPING
# ============================================================

def validate_mapping(
    faiss_index,
    metadata,
    bm25,
    bm25_metadata
):

    print()
    print(
        "GLOBAL MAPPING VALIDATION"
    )
    print("-" * 80)

    print(
        f"FAISS vectors       : "
        f"{faiss_index.ntotal}"
    )

    print(
        f"V1 metadata records : "
        f"{len(metadata)}"
    )

    print(
        f"BM25 documents      : "
        f"{len(bm25.doc_freqs)}"
    )

    print(
        f"BM25 metadata       : "
        f"{len(bm25_metadata)}"
    )

    if faiss_index.ntotal != len(metadata):

        raise ValueError(
            "FAISS vectors and V1 metadata "
            "counts do not match."
        )

    if len(bm25.doc_freqs) != len(bm25_metadata):

        raise ValueError(
            "BM25 documents and BM25 metadata "
            "counts do not match."
        )

    if len(metadata) != len(bm25_metadata):

        raise ValueError(
            "Dense metadata and BM25 metadata "
            "counts do not match."
        )

    print()
    print(
        "Mapping validation: OK"
    )


# ============================================================
# RRF HYBRID RETRIEVAL
# ============================================================

def hybrid_rrf(
    dense_results,
    bm25_results
):

    candidates = {}

    # ========================================================
    # DENSE RESULTS
    # ========================================================

    for result in dense_results:

        vector_id = result[
            "vector_id"
        ]

        if vector_id not in candidates:

            candidates[vector_id] = {

                "vector_id": vector_id,

                "dense_rank": None,

                "dense_score": None,

                "bm25_rank": None,

                "bm25_score": None,

                "rrf_score": 0.0

            }

        candidates[vector_id][
            "dense_rank"
        ] = result["dense_rank"]

        candidates[vector_id][
            "dense_score"
        ] = result["dense_score"]


    # ========================================================
    # BM25 RESULTS
    # ========================================================

    for result in bm25_results:

        vector_id = result[
            "vector_id"
        ]

        if vector_id not in candidates:

            candidates[vector_id] = {

                "vector_id": vector_id,

                "dense_rank": None,

                "dense_score": None,

                "bm25_rank": None,

                "bm25_score": None,

                "rrf_score": 0.0

            }

        candidates[vector_id][
            "bm25_rank"
        ] = result["bm25_rank"]

        candidates[vector_id][
            "bm25_score"
        ] = result["bm25_score"]


    # ========================================================
    # CALCULATE RRF
    # ========================================================

    for candidate in candidates.values():

        score = 0.0

        dense_rank = candidate[
            "dense_rank"
        ]

        bm25_rank = candidate[
            "bm25_rank"
        ]

        if dense_rank is not None:

            score += 1.0 / (
                RRF_K + dense_rank
            )

        if bm25_rank is not None:

            score += 1.0 / (
                RRF_K + bm25_rank
            )

        candidate[
            "rrf_score"
        ] = score


    # ========================================================
    # SORT
    # ========================================================

    ranked_candidates = sorted(
        candidates.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )

    return ranked_candidates


# ============================================================
# DIVERSIFY RESULTS BY JUDGMENT
# ============================================================

def diversify_by_judgment(
    candidates,
    metadata
):

    final_results = []

    judgment_counts = {}

    for candidate in candidates:

        vector_id = candidate[
            "vector_id"
        ]

        if vector_id >= len(metadata):
            continue

        chunk = metadata[
            vector_id
        ]

        # Use document_id as judgment identifier
        judgment_id = (
            chunk.get("parent_document_id")
            or chunk.get("document_id")
            or chunk.get("case_title")
        )

        current_count = judgment_counts.get(
            judgment_id,
            0
        )

        if current_count >= MAX_CHUNKS_PER_JUDGMENT:

            continue

        candidate = candidate.copy()

        candidate["chunk"] = chunk

        final_results.append(
            candidate
        )

        judgment_counts[
            judgment_id
        ] = current_count + 1

        if len(final_results) >= HYBRID_TOP_K:

            break

    return final_results


# ============================================================
# CLEAN TEXT FOR DISPLAY
# ============================================================

def clean_display_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    query,
    results
):

    print()
    print("=" * 100)
    print("LEGAL JUDGMENT HYBRID SEARCH RESULTS")
    print("=" * 100)

    print()
    print("QUERY")
    print("-" * 100)
    print(query)

    print()
    print("RETRIEVAL CONFIGURATION")
    print("-" * 100)

    print(
        f"Dense candidates       : "
        f"{DENSE_TOP_K}"
    )

    print(
        f"BM25 candidates        : "
        f"{BM25_TOP_K}"
    )

    print(
        f"Final results           : "
        f"{len(results)}"
    )

    print(
        f"Max chunks / judgment  : "
        f"{MAX_CHUNKS_PER_JUDGMENT}"
    )

    print(
        f"RRF constant            : "
        f"{RRF_K}"
    )

    print("=" * 100)


    # ========================================================
    # RESULTS
    # ========================================================

    for rank, result in enumerate(
        results,
        start=1
    ):

        chunk = result["chunk"]

        case_title = (
            chunk.get("case_title")
            or "Not available"
        )

        date = (
            chunk.get("date")
            or "Not available"
        )

        citation = (
            chunk.get("citation")
            or "Not available"
        )

        chunk_index = (
            chunk.get("chunk_index")
        )

        word_count = (
            chunk.get("word_count")
        )


        print()
        print(
            f"RESULT #{rank}"
        )

        print("-" * 100)

        print(
            f"Case       : {case_title}"
        )

        print(
            f"Date       : {date}"
        )

        print(
            f"Citation   : {citation}"
        )

        print(
            f"Chunk      : {chunk_index}"
        )

        print(
            f"Word Count : {word_count}"
        )


        print()
        print(
            "RETRIEVAL INFORMATION"
        )

        print(
            f"Hybrid Rank : {rank}"
        )

        print(
            f"RRF Score   : "
            f"{result['rrf_score']:.6f}"
        )


        if result["dense_rank"] is not None:

            print(
                f"Dense Rank : "
                f"{result['dense_rank']}"
            )

            print(
                f"Dense Score: "
                f"{result['dense_score']:.4f}"
            )

        else:

            print(
                "Dense Rank : Not retrieved"
            )

            print(
                "Dense Score: N/A"
            )


        if result["bm25_rank"] is not None:

            print(
                f"BM25 Rank  : "
                f"{result['bm25_rank']}"
            )

            print(
                f"BM25 Score : "
                f"{result['bm25_score']:.4f}"
            )

        else:

            print(
                "BM25 Rank  : Not retrieved"
            )

            print(
                "BM25 Score : N/A"
            )


        print()
        print("EVIDENCE")
        print("-" * 100)

        text = clean_display_text(
            chunk.get("text", "")
        )

        if text:

            preview = text[:700]

            wrapped_lines = textwrap.wrap(
                preview,
                width=96,
                break_long_words=False,
                break_on_hyphens=False
            )

            for line in wrapped_lines:

                print(
                    f"  {line}"
                )

            if len(text) > 700:

                print()
                print(
                    "  ... [preview truncated]"
                )

        else:

            print(
                "  No text available."
            )

        print("-" * 100)


    print()
    print("=" * 100)
    print("END OF RESULTS")
    print("=" * 100)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 100)
    print(
        "LEGAL JUDGMENT HYBRID RETRIEVAL - V1"
    )
    print("=" * 100)

    print(
        f"Device: {DEVICE}"
    )

    print()


    # ========================================================
    # LOAD EVERYTHING
    # ========================================================

    tokenizer, model = load_model()

    print()

    faiss_index = load_faiss()

    print()

    metadata = load_metadata()

    print()

    bm25, bm25_metadata = load_bm25()

    print()


    # ========================================================
    # GLOBAL VALIDATION
    # ========================================================

    validate_mapping(
        faiss_index,
        metadata,
        bm25,
        bm25_metadata
    )

    print()
    print("=" * 100)


    # ========================================================
    # INTERACTIVE SEARCH
    # ========================================================

    while True:

        print()

        query = input(
            "Enter legal query "
            "(type 'exit' to quit):\n> "
        ).strip()


        if query.lower() == "exit":

            print()
            print("Exiting.")

            break


        if not query:

            print()
            print(
                "Please enter a query."
            )

            continue


        # ====================================================
        # DENSE RETRIEVAL
        # ====================================================

        print()
        print(
            "Running dense retrieval..."
        )

        dense_results = dense_search(
            query,
            faiss_index,
            metadata,
            tokenizer,
            model
        )

        print(
            f"Dense results: "
            f"{len(dense_results)}"
        )


        # ====================================================
        # BM25 RETRIEVAL
        # ====================================================

        print()
        print(
            "Running BM25 retrieval..."
        )

        bm25_results = bm25_search(
            query,
            bm25,
            bm25_metadata
        )

        print(
            f"BM25 results: "
            f"{len(bm25_results)}"
        )


        # ====================================================
        # RRF
        # ====================================================

        print()
        print(
            "Combining candidates using RRF..."
        )

        hybrid_candidates = hybrid_rrf(
            dense_results,
            bm25_results
        )

        print(
            f"Combined candidate pool: "
            f"{len(hybrid_candidates)}"
        )


        # ====================================================
        # DIVERSIFICATION
        # ====================================================

        final_results = diversify_by_judgment(
            hybrid_candidates,
            metadata
        )

        print(
            f"Final diversified candidates: "
            f"{len(final_results)}"
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        display_results(
            query,
            final_results
        )

        print("\n" + "=" * 80)
        print("EXPLAINABILITY FEATURE EXTRACTION")
        print("=" * 80)

        for rank, result in enumerate(
            final_results[:10],
            start=1
        ):
            features = extract_features(
                query,
                result
            )

            case_title = result["chunk"].get(
                "case_title",
                "Unknown"
            )

            print(f"\nRESULT #{rank}")
            print(f"Case: {case_title}")

            print("\nExtracted Features:")

            for feature_name, value in features.items():
                print(f"  {feature_name}: {value}")

            print("-" * 80)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
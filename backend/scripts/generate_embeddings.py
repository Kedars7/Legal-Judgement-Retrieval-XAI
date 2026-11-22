import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "law-ai/InLegalBERT"

INPUT_DIR = Path("data/processed/final_chunks")
OUTPUT_DIR = Path("embeddings")

BATCH_SIZE = 8
MAX_LENGTH = 512

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# MEAN POOLING
# ============================================================

def mean_pooling(last_hidden_state, attention_mask):
    """
    Mean-pool token embeddings while ignoring padding tokens.
    """

    mask = attention_mask.unsqueeze(-1).expand(
        last_hidden_state.size()
    ).float()

    summed = torch.sum(
        last_hidden_state * mask,
        dim=1
    )

    counts = torch.clamp(
        mask.sum(dim=1),
        min=1e-9
    )

    return summed / counts


# ============================================================
# LOAD ALL CHUNKS
# ============================================================

def load_chunks():

    files = sorted(
        INPUT_DIR.glob("*.json")
    )

    print(f"Judgment files found: {len(files)}")

    all_chunks = []

    for i, file_path in enumerate(files, start=1):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        for chunk in data.get("chunks", []):

            all_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "year": chunk.get("year"),
                "pages": chunk.get("pages"),
                "case_title": chunk.get("case_title"),
                "date": chunk.get("date"),
                "citation": chunk.get("citation"),
                "bench": chunk.get("bench"),
                "petitioner": chunk.get("petitioner"),
                "respondent": chunk.get("respondent"),
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"]
            })

        if i % 500 == 0 or i == len(files):
            print(
                f"Loaded {i}/{len(files)} judgments | "
                f"Chunks: {len(all_chunks)}"
            )

    return all_chunks


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

def generate_embeddings(
    chunks,
    tokenizer,
    model
):

    embeddings = []

    total = len(chunks)

    print()
    print(f"Generating embeddings for {total} chunks...")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Max tokens: {MAX_LENGTH}")
    print()

    for start in range(
        0,
        total,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total
        )

        batch = chunks[start:end]

        texts = [
            item["text"]
            for item in batch
        ]

        # ----------------------------------------------------
        # TOKENIZATION
        # ----------------------------------------------------

        encoded = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )

        encoded = {
            key: value.to(DEVICE)
            for key, value in encoded.items()
        }

        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        with torch.no_grad():

            output = model(
                **encoded
            )

            batch_embeddings = mean_pooling(
                output.last_hidden_state,
                encoded["attention_mask"]
            )

            # Normalize for cosine similarity / inner product
            batch_embeddings = torch.nn.functional.normalize(
                batch_embeddings,
                p=2,
                dim=1
            )

        # Move from GPU to CPU
        batch_embeddings = (
            batch_embeddings
            .cpu()
            .numpy()
            .astype(np.float32)
        )

        embeddings.append(
            batch_embeddings
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if (
            end % 800 == 0
            or end == total
        ):

            percent = (
                end / total
            ) * 100

            print(
                f"Processed {end}/{total} "
                f"({percent:.2f}%)"
            )

    return np.vstack(embeddings)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("INLEGALBERT FULL EMBEDDING GENERATION")
    print("=" * 70)

    print(f"Device: {DEVICE}")

    if DEVICE.type == "cuda":
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

        print(
            f"CUDA memory: "
            f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB"
        )

    print()

    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print("Loading model...")

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    model.to(DEVICE)
    model.eval()

    print("Model loaded successfully.")
    print()

    # --------------------------------------------------------
    # LOAD CHUNKS
    # --------------------------------------------------------

    chunks = load_chunks()

    if not chunks:
        print("No chunks found.")
        return

    print()
    print(f"Total chunks: {len(chunks)}")

    # --------------------------------------------------------
    # GENERATE EMBEDDINGS
    # --------------------------------------------------------

    embeddings = generate_embeddings(
        chunks,
        tokenizer,
        model
    )

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("VERIFYING EMBEDDINGS")
    print("=" * 70)

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    print(
        f"Data type: {embeddings.dtype}"
    )

    first_norm = np.linalg.norm(
        embeddings[0]
    )

    print(
        f"First embedding norm: {first_norm:.6f}"
    )

    # --------------------------------------------------------
    # SAVE EMBEDDINGS
    # --------------------------------------------------------

    embedding_path = (
        OUTPUT_DIR / "embeddings.npy"
    )

    print()
    print(
        f"Saving embeddings to:\n{embedding_path}"
    )

    np.save(
        embedding_path,
        embeddings
    )

    # --------------------------------------------------------
    # SAVE METADATA / MAPPING
    # --------------------------------------------------------

    metadata = []

    for chunk in chunks:

        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "source_file": chunk["source_file"],
            "year": chunk["year"],
            "pages": chunk["pages"],
            "case_title": chunk["case_title"],
            "date": chunk["date"],
            "citation": chunk["citation"],
            "bench": chunk["bench"],
            "petitioner": chunk["petitioner"],
            "respondent": chunk["respondent"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"]
        })

    metadata_path = (
        OUTPUT_DIR / "metadata.json"
    )

    print(
        f"Saving metadata to:\n{metadata_path}"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Total embeddings: {len(embeddings)}"
    )

    print(
        f"Embedding dimensions: {embeddings.shape[1]}"
    )

    print()
    print("Files created:")

    print(
        f"  {embedding_path}"
    )

    print(
        f"  {metadata_path}"
    )


if __name__ == "__main__":
    main()
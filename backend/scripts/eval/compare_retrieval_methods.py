
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# Add project root to Python path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.testing.search_hybrid import (
    DENSE_TOP_K,
    BM25_TOP_K,
    MAX_CHUNKS_PER_JUDGMENT,
    RRF_K,
    load_model,
    load_faiss,
    load_metadata,
    load_bm25,
    dense_search,
    bm25_search,
    hybrid_rrf,
    diversify_by_judgment,
    validate_mapping,
)

from scripts.eval.create_relevance_dataset import QUERIES


OUTPUT_DIR = PROJECT_ROOT / "eval" / "retrieval_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_DIR / "retrieval_results.csv"
SUMMARY_JSON = OUTPUT_DIR / "retrieval_summary.json"

FINAL_K = 10


def judgment_id_for(vector_id, metadata):
    chunk = metadata[vector_id]
    return (
        chunk.get("parent_document_id")
        or chunk.get("document_id")
        or chunk.get("case_title")
        or f"vector_{vector_id}"
    )


def diversify_ranked_results(results, metadata, limit=FINAL_K):
    """Apply the same judgment-level diversity rule to each method."""
    selected = []
    counts = defaultdict(int)

    for result in results:
        vector_id = int(result["vector_id"])

        if vector_id < 0 or vector_id >= len(metadata):
            continue

        jid = judgment_id_for(vector_id, metadata)

        if counts[jid] >= MAX_CHUNKS_PER_JUDGMENT:
            continue

        row = dict(result)
        row["chunk"] = metadata[vector_id]
        selected.append(row)
        counts[jid] += 1

        if len(selected) >= limit:
            break

    return selected


def result_metadata(result):
    chunk = result["chunk"]

    return {
        "document_id": chunk.get("document_id", ""),
        "parent_document_id": chunk.get("parent_document_id", ""),
        "case_title": chunk.get("case_title", ""),
        "chunk_id": chunk.get("chunk_id", ""),
        "evidence": (
            chunk.get("text")
            or chunk.get("chunk_text")
            or chunk.get("content")
            or ""
        ),
    }


def main():
    print("=" * 75)
    print("SEMANTIC vs BM25 vs HYBRID RETRIEVAL")
    print("=" * 75)

    tokenizer, model = load_model()
    index = load_faiss()
    metadata = load_metadata()
    bm25, bm25_metadata = load_bm25()

    validate_mapping(index, metadata, bm25, bm25_metadata)

    if len(metadata) != len(bm25_metadata):
        raise ValueError("Dense and BM25 metadata lengths differ.")

    rows = []
    summary = {
        "experiment": "Semantic vs BM25 vs Hybrid RRF",
        "query_count": len(QUERIES),
        "final_k": FINAL_K,
        "dense_top_k": DENSE_TOP_K,
        "bm25_top_k": BM25_TOP_K,
        "rrf_k": RRF_K,
        "max_chunks_per_judgment": MAX_CHUNKS_PER_JUDGMENT,
        "methods": {},
        "notes": [
            "This experiment records retrieval rankings and scores.",
            "It does not claim relevance-based superiority without "
            "common relevance labels for all returned candidates."
        ],
    }

    method_counts = defaultdict(list)

    for query_id, query in enumerate(QUERIES, start=1):
        print(f"\n[{query_id}/{len(QUERIES)}] {query}")

        dense_results = dense_search(
            query, index, metadata, tokenizer, model
        )

        lexical_results = bm25_search(
            query, bm25, metadata
        )

        hybrid_candidates = hybrid_rrf(
            dense_results, lexical_results
        )

        methods = {
            "semantic": diversify_ranked_results(
                dense_results, metadata
            ),
            "bm25": diversify_ranked_results(
                lexical_results, metadata
            ),
            "hybrid_rrf": diversify_ranked_results(
                hybrid_candidates, metadata
            ),
        }

        for method, results in methods.items():
            method_counts[method].append(len(results))

            for rank, result in enumerate(results, start=1):
                details = result_metadata(result)

                rows.append({
                    "query_id": query_id,
                    "query": query,
                    "method": method,
                    "rank": rank,
                    "vector_id": result["vector_id"],
                    "dense_score": result.get("dense_score"),
                    "dense_rank": result.get("dense_rank"),
                    "bm25_score": result.get("bm25_score"),
                    "bm25_rank": result.get("bm25_rank"),
                    "rrf_score": result.get("rrf_score"),
                    **details,
                })

        print(
            "  Returned: "
            + ", ".join(
                f"{method}={len(results)}"
                for method, results in methods.items()
            )
        )

    fieldnames = [
        "query_id", "query", "method", "rank", "vector_id",
        "document_id", "parent_document_id", "case_title",
        "chunk_id", "dense_score", "dense_rank", "bm25_score",
        "bm25_rank", "rrf_score", "evidence",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    for method, counts in method_counts.items():
        summary["methods"][method] = {
            "queries": len(counts),
            "mean_results_returned": (
                float(np.mean(counts)) if counts else 0.0
            ),
            "total_results": int(sum(counts)),
        }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75)
    print("EXPERIMENT COMPLETE")
    print("=" * 75)
    print(f"Ranked results CSV : {OUTPUT_CSV}")
    print(f"Summary JSON       : {SUMMARY_JSON}")
    print(f"Rows exported      : {len(rows)}")

    print("\nResults by method:")
    for method, stats in summary["methods"].items():
        print(
            f"  {method:12s} | "
            f"total={stats['total_results']:4d} | "
            f"mean/query={stats['mean_results_returned']:.2f}"
        )


if __name__ == "__main__":
    main()

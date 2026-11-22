
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.testing.search_hybrid import (
    DENSE_TOP_K,
    BM25_TOP_K,
    MAX_CHUNKS_PER_JUDGMENT,
    load_model,
    load_faiss,
    load_metadata,
    load_bm25,
    dense_search,
    bm25_search,
    hybrid_rrf,
    validate_mapping,
)

from scripts.eval.create_relevance_dataset import QUERIES
from scripts.eval.evaluate_pooled_retrieval import (
    load_judgments,
    calculate_metrics,
)

OUTPUT_DIR = PROJECT_ROOT / "eval" / "hybrid_rrf_tuning"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_K = 10

# Keep the first configuration as the baseline.
CONFIGS = [
    {"name": "baseline_1_1", "dense": 1.0, "bm25": 1.0},
    {"name": "dense_075_bm25_125", "dense": 0.75, "bm25": 1.25},
    {"name": "dense_050_bm25_150", "dense": 0.50, "bm25": 1.50},
    {"name": "dense_025_bm25_175", "dense": 0.25, "bm25": 1.75},
    {"name": "dense_125_bm25_075", "dense": 1.25, "bm25": 0.75},
]


def judgment_id_for(vector_id, metadata):
    chunk = metadata[vector_id]
    return (
        chunk.get("parent_document_id")
        or chunk.get("document_id")
        or chunk.get("case_title")
        or f"vector_{vector_id}"
    )


def diversify(results, metadata):
    selected = []
    counts = {}

    for result in results:
        vector_id = int(result["vector_id"])

        if not 0 <= vector_id < len(metadata):
            continue

        judgment_id = judgment_id_for(vector_id, metadata)
        count = counts.get(judgment_id, 0)

        if count >= MAX_CHUNKS_PER_JUDGMENT:
            continue

        row = dict(result)
        row["chunk"] = metadata[vector_id]
        selected.append(row)
        counts[judgment_id] = count + 1

        if len(selected) >= FINAL_K:
            break

    return selected


def main():
    print("Loading retrieval components...")

    tokenizer, model = load_model()
    index = load_faiss()
    metadata = load_metadata()
    bm25, bm25_metadata = load_bm25()

    validate_mapping(index, metadata, bm25, bm25_metadata)

    if len(metadata) != len(bm25_metadata):
        raise ValueError("Dense and BM25 metadata lengths differ.")

    # Load the exact existing relevance judgments.
    labels = load_judgments()
    labels["query_id"] = labels["query_id"].astype(str).str.strip()
    labels["chunk_id"] = labels["chunk_id"].astype(str).str.strip()

    label_map = {
        (row.query_id, row.chunk_id): int(row.relevance)
        for row in labels.itertuples(index=False)
    }

    relevant_per_query = (
        labels.groupby("query_id")["relevance"].sum().to_dict()
    )

    all_results = []
    all_unjudged = []

    # Cache retriever outputs so every weight configuration receives
    # precisely the same dense and BM25 candidate rankings.
    cached_queries = []

    for query_id, query in enumerate(QUERIES, start=1):
        print(f"Caching query {query_id}/{len(QUERIES)}")

        dense_results = dense_search(
            query, index, metadata, tokenizer, model
        )
        lexical_results = bm25_search(query, bm25, bm25_metadata)

        cached_queries.append(
            (str(query_id), query, dense_results, lexical_results)
        )

    for config in CONFIGS:
        print(f"\nEvaluating {config['name']}")

        for query_id, query, dense_results, lexical_results in cached_queries:
            candidates = hybrid_rrf(
                dense_results,
                lexical_results,
                dense_weight=config["dense"],
                bm25_weight=config["bm25"],
                rrf_k=60,
            )

            results = diversify(candidates, metadata)

            for rank, result in enumerate(results, start=1):
                chunk = result["chunk"]
                chunk_id = str(chunk.get("chunk_id", "")).strip()
                key = (query_id, chunk_id)

                row = {
                    "config": config["name"],
                    "query_id": query_id,
                    "query": query,
                    "rank": rank,
                    "vector_id": result["vector_id"],
                    "chunk_id": chunk_id,
                    "case_title": chunk.get("case_title", ""),
                    "document_id": chunk.get("document_id", ""),
                    "parent_document_id": chunk.get(
                        "parent_document_id", ""
                    ),
                    "rrf_score": result["rrf_score"],
                    "dense_rank": result.get("dense_rank"),
                    "bm25_rank": result.get("bm25_rank"),
                }

                all_results.append(row)

                if key not in label_map:
                    all_unjudged.append(row.copy())
                else:
                    row["relevance"] = label_map[key]

    results_df = pd.DataFrame(all_results)
    results_path = OUTPUT_DIR / "tuning_results.csv"
    results_df.to_csv(results_path, index=False)

    if all_unjudged:
        unjudged_df = pd.DataFrame(all_unjudged)
        unjudged_path = OUTPUT_DIR / "unjudged_candidates.csv"
        unjudged_df.to_csv(unjudged_path, index=False)

        print("\nSTOP: evaluation is incomplete.")
        print(f"Unjudged result rows: {len(unjudged_df)}")
        print(f"Unique unjudged query/chunk pairs: "
              f"{unjudged_df[['query_id', 'chunk_id']].drop_duplicates().shape[0]}")
        print(f"Review candidates: {unjudged_path}")
        print("Do not calculate or compare scores until these candidates "
              "have been judged and the script rerun.")
        return

    per_query_rows = []

    for config in CONFIGS:
        config_df = results_df[
            results_df["config"] == config["name"]
        ].copy()

        for query_id, group in config_df.groupby("query_id"):
            # Existing metric definitions are reused unchanged.
            metrics = calculate_metrics(
                group.rename(columns={"relevance": "relevance"}),
                int(relevant_per_query.get(query_id, 0)),
            )

            per_query_rows.append({
                "config": config["name"],
                "query_id": query_id,
                **metrics,
            })

    per_query_df = pd.DataFrame(per_query_rows)
    per_query_df.to_csv(
        OUTPUT_DIR / "per_query_metrics.csv", index=False
    )

    metric_columns = [
        "precision@5",
        "precision@10",
        "recall@10",
        "map@10",
        "ndcg@10",
        "mrr",
    ]

    summary = (
        per_query_df.groupby("config")[metric_columns]
        .mean()
        .reset_index()
    )

    summary.to_csv(
        OUTPUT_DIR / "tuning_summary.csv", index=False
    )

    print("\nMean metrics by configuration:")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nSaved results to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()


from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

RETRIEVAL_FILE = (
    ROOT / "eval" / "retrieval_comparison" / "retrieval_results.csv"
)
EXISTING_LABELS_FILE = ROOT / "eval" / "relevance_dataset_labeled.csv"
FINAL_LABELS_FILE = (
    ROOT / "eval" / "pooled_evaluation" / "candidates_to_review_final.csv"
)

OUTPUT_DIR = ROOT / "eval" / "pooled_evaluation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

METHODS = ["semantic", "bm25", "hybrid_rrf"]
K_VALUES = [5, 10]


def normalize_keys(df):
    df = df.copy()
    df["query_id"] = df["query_id"].astype(str).str.strip()
    df["chunk_id"] = df["chunk_id"].astype(str).str.strip()
    return df


def load_judgments():
    existing = pd.read_csv(EXISTING_LABELS_FILE)
    reviewed = pd.read_csv(FINAL_LABELS_FILE)

    required = {"query_id", "chunk_id", "relevance"}
    for name, df in [
        ("Existing labels", existing),
        ("Final reviewed labels", reviewed),
    ]:
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")

    existing = normalize_keys(existing)
    reviewed = normalize_keys(reviewed)

    # Keep only actual relevance judgments.
    existing = existing.dropna(subset=["relevance"])
    reviewed = reviewed.dropna(subset=["relevance"])

    existing["relevance"] = pd.to_numeric(
        existing["relevance"], errors="raise"
    )
    reviewed["relevance"] = pd.to_numeric(
        reviewed["relevance"], errors="raise"
    )

    for name, df in [
        ("Existing labels", existing),
        ("Final reviewed labels", reviewed),
    ]:
        if not df["relevance"].isin([0, 1]).all():
            raise ValueError(f"{name} contains labels other than 0 or 1.")

    # Combine judgments, retaining the source for auditing.
    labels = pd.concat(
        [
            existing[["query_id", "chunk_id", "relevance"]].assign(
                label_source="existing"
            ),
            reviewed[["query_id", "chunk_id", "relevance"]].assign(
                label_source="reviewed"
            ),
        ],
        ignore_index=True,
    )

    # Never silently resolve disagreements between annotators/sources.
    conflicts = (
        labels.groupby(["query_id", "chunk_id"])["relevance"]
        .nunique()
    )
    conflicts = conflicts[conflicts > 1]

    if not conflicts.empty:
        raise ValueError(
            "Conflicting labels found. Resolve these before evaluation:\n"
            + conflicts.to_string()
        )

    labels = labels.drop_duplicates(
        subset=["query_id", "chunk_id"]
    )

    print("Unique judged candidates:", len(labels))
    print("Relevant candidates:", int(labels["relevance"].sum()))
    print(
        "Non-relevant candidates:",
        int((labels["relevance"] == 0).sum()),
    )

    return labels[["query_id", "chunk_id", "relevance"]]


def dcg_at_k(relevances, k):
    relevances = np.asarray(relevances[:k], dtype=float)
    if len(relevances) == 0:
        return 0.0

    discounts = np.log2(np.arange(2, len(relevances) + 2))
    return float(np.sum(relevances / discounts))


def calculate_metrics(group, total_relevant):
    group = group.sort_values("rank")
    relevance = group["relevance"].to_numpy(dtype=int)

    metrics = {}

    for k in K_VALUES:
        top = relevance[:k]
        hits = int(top.sum())

        # Precision denominator is k, even if fewer than k results exist.
        metrics[f"precision@{k}"] = hits / k

        if k == 10:
            metrics["recall@10"] = (
                hits / total_relevant if total_relevant else 0.0
            )

            cumulative_hits = np.cumsum(top)
            positions = np.arange(1, len(top) + 1)
            precision_at_positions = cumulative_hits / positions

            # AP@10: normalize by relevant candidates up to the cutoff.
            denominator = min(total_relevant, k)
            metrics["map@10"] = (
                float(
                    np.sum(precision_at_positions * top) / denominator
                )
                if denominator > 0
                else 0.0
            )

            ideal = np.ones(min(total_relevant, k), dtype=int)
            ideal_dcg = dcg_at_k(ideal, k)
            actual_dcg = dcg_at_k(top, k)

            metrics["ndcg@10"] = (
                actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0
            )

    relevant_positions = np.flatnonzero(relevance == 1)
    metrics["mrr"] = (
        1.0 / (relevant_positions[0] + 1)
        if len(relevant_positions)
        else 0.0
    )

    return metrics


def main():
    retrieval = pd.read_csv(RETRIEVAL_FILE)
    required = {"query_id", "chunk_id", "method", "rank"}

    missing = required - set(retrieval.columns)
    if missing:
        raise ValueError(
            f"Retrieval results missing columns: {sorted(missing)}"
        )

    retrieval = normalize_keys(retrieval)
    retrieval["rank"] = pd.to_numeric(
        retrieval["rank"], errors="raise"
    )

    labels = load_judgments()

    # Merge judgments into every method's original ranked results.
    evaluated = retrieval.merge(
        labels,
        on=["query_id", "chunk_id"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unjudged = evaluated[evaluated["_merge"] != "both"]
    if not unjudged.empty:
        unjudged[
            ["query_id", "method", "rank", "chunk_id"]
        ].to_csv(OUTPUT_DIR / "unjudged_results.csv", index=False)

        raise ValueError(
            f"{len(unjudged)} retrieval rows have no relevance label. "
            "See eval/pooled_evaluation/unjudged_results.csv. "
            "Do not treat unjudged candidates as irrelevant."
        )

    evaluated = evaluated.drop(columns="_merge")
    evaluated["relevance"] = evaluated["relevance"].astype(int)

    # Check that each query/method has unique ranks.
    if evaluated.duplicated(["query_id", "method", "rank"]).any():
        raise ValueError("Duplicate ranks found for a query/method.")

    evaluated.to_csv(
        OUTPUT_DIR / "evaluated_retrieval_results.csv", index=False
    )

    # Total relevant judgments per query in the pooled candidate set.
    relevant_per_query = (
        labels.groupby("query_id")["relevance"].sum().to_dict()
    )

    per_query_rows = []

    for (method, query_id), group in evaluated.groupby(
        ["method", "query_id"]
    ):
        if method not in METHODS:
            continue

        metrics = calculate_metrics(
            group,
            int(relevant_per_query.get(query_id, 0)),
        )

        per_query_rows.append(
            {
                "method": method,
                "query_id": query_id,
                "total_relevant_in_pool": int(
                    relevant_per_query.get(query_id, 0)
                ),
                "result_count": len(group),
                **metrics,
            }
        )

    per_query = pd.DataFrame(per_query_rows)
    per_query.to_csv(
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
        per_query.groupby("method")[metric_columns]
        .mean()
        .reindex(METHODS)
        .reset_index()
    )

    summary.to_csv(
        OUTPUT_DIR / "retrieval_metrics_summary.csv", index=False
    )

    print("\nEvaluated result rows:", len(evaluated))
    print("Queries per method:")
    print(per_query.groupby("method")["query_id"].nunique().to_string())

    print("\nMean metrics by method:")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\nOutput files:")
    print(OUTPUT_DIR / "evaluated_retrieval_results.csv")
    print(OUTPUT_DIR / "per_query_metrics.csv")
    print(OUTPUT_DIR / "retrieval_metrics_summary.csv")


if __name__ == "__main__":
    main()

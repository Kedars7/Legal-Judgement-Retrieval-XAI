
import pandas as pd
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_PATH = (
    PROJECT_ROOT
    / "eval"
    / "retrieval_comparison"
    / "retrieval_results.csv"
)

LABELED_PATH = (
    PROJECT_ROOT
    / "eval"
    / "relevance_dataset_labeled.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "eval"
    / "pooled_evaluation"
)

POOLED_PATH = OUTPUT_DIR / "pooled_candidates.csv"
REVIEW_PATH = OUTPUT_DIR / "candidates_to_review.csv"
SUMMARY_PATH = OUTPUT_DIR / "pooling_summary.txt"

KEYS = ["query_id", "chunk_id"]


def main():
    print("=" * 70)
    print("PREPARING POOLED RELEVANCE EVALUATION")
    print("=" * 70)

    results = pd.read_csv(RESULTS_PATH)
    labels = pd.read_csv(LABELED_PATH)

    # --------------------------------------------------------
    # Validate input data
    # --------------------------------------------------------

    required_results = {
        "query_id", "query", "method", "rank",
        "chunk_id", "case_title", "evidence"
    }
    required_labels = {
        "query_id", "chunk_id", "relevance"
    }

    if not required_results.issubset(results.columns):
        raise ValueError(
            f"Missing retrieval columns: "
            f"{required_results - set(results.columns)}"
        )

    if not required_labels.issubset(labels.columns):
        raise ValueError(
            f"Missing label columns: "
            f"{required_labels - set(labels.columns)}"
        )

    if results[KEYS].isna().any().any():
        raise ValueError("Retrieval data contains missing join keys.")

    if labels[KEYS].isna().any().any():
        raise ValueError("Label data contains missing join keys.")

    # --------------------------------------------------------
    # Resolve duplicate label keys safely
    # --------------------------------------------------------

    labels["relevance"] = pd.to_numeric(
        labels["relevance"],
        errors="coerce"
    )

    labeled_rows = labels.dropna(
        subset=["relevance"]
    ).copy()

    invalid_labels = ~labeled_rows["relevance"].isin([0, 1])

    if invalid_labels.any():
        raise ValueError(
            "Relevance labels must be 0 or 1."
        )

    conflicts = (
        labeled_rows.groupby(KEYS)["relevance"]
        .nunique()
    )

    if (conflicts > 1).any():
        raise ValueError(
            "Conflicting relevance labels exist. "
            "Resolve them before continuing."
        )

    # Keep one row per query/chunk key.
    # All duplicate keys must agree on relevance.
    labels_unique = labeled_rows.drop_duplicates(
        subset=KEYS,
        keep="first"
    )

    # --------------------------------------------------------
    # Build a unique candidate pool
    # --------------------------------------------------------

    pooled = results.drop_duplicates(
        subset=KEYS,
        keep="first"
    ).copy()

    # Retain the original retrieval method/rank rows separately.
    # They are required for calculating metrics later.
    pooled = pooled.merge(
        labels_unique[KEYS + ["relevance"]],
        on=KEYS,
        how="left",
        validate="one_to_one"
    )

    pooled["label_status"] = pooled["relevance"].map(
        {0: "judged_not_relevant", 1: "judged_relevant"}
    ).fillna("needs_review")

    # Review file should contain only previously unlabeled candidates.
    review = pooled.loc[
        pooled["relevance"].isna(),
        [
            "query_id",
            "query",
            "chunk_id",
            "case_title",
            "evidence",
            "label_status",
        ],
    ].copy()

    # Blank column for human judgments.
    review["relevance"] = ""
    review["label_reason"] = ""

    # --------------------------------------------------------
    # Save artifacts
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pooled.to_csv(POOLED_PATH, index=False)
    review.to_csv(REVIEW_PATH, index=False)

    summary_lines = [
        "POOLED RELEVANCE EVALUATION PREPARATION",
        "",
        f"Retrieval rows: {len(results)}",
        f"Unique query/chunk candidates: {len(pooled)}",
        f"Unique queries: {pooled['query_id'].nunique()}",
        "",
        "Candidates by method before pooling:",
    ]

    summary_lines.extend(
        f"{method}: {count}"
        for method, count in
        results.groupby("method").size().items()
    )

    summary_lines.extend([
        "",
        f"Previously judged pooled candidates: "
        f"{pooled['relevance'].notna().sum()}",
        f"Candidates needing review: {len(review)}",
        "",
        "Files:",
        str(POOLED_PATH),
        str(REVIEW_PATH),
        "",
        "No relevance metrics were calculated.",
        "Unjudged candidates must not be treated as irrelevant.",
    ])

    SUMMARY_PATH.write_text(
        "\n".join(summary_lines),
        encoding="utf-8"
    )

    print()
    print(f"Retrieval rows: {len(results)}")
    print(f"Unique pooled candidates: {len(pooled)}")
    print(
        "Previously judged candidates:",
        int(pooled["relevance"].notna().sum())
    )
    print(f"Candidates needing review: {len(review)}")

    print()
    print("OUTPUT FILES")
    print(POOLED_PATH)
    print(REVIEW_PATH)
    print(SUMMARY_PATH)

    print()
    print("Preparation complete.")
    print("No existing files were modified.")


if __name__ == "__main__":
    main()

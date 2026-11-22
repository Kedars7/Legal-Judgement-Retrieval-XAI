from pathlib import Path
import json

import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = Path(
    "eval/retrieval_explanations.csv"
)

OUTPUT_PATH = Path(
    "eval/candidate_explanations.json"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("BUILDING CANDIDATE-LEVEL EXPLANATIONS")
print("=" * 70)

df = pd.read_csv(INPUT_PATH)

print(f"\nExplanation rows: {len(df)}")


# ============================================================
# BUILD CANDIDATE GROUPS
# ============================================================

candidate_groups = df.groupby(
    [
        "query_id",
        "candidate_rank",
        "case_title",
        "document_id",
        "chunk_id",
    ],
    dropna=False,
)


results = []


for group_key, group in candidate_groups:

    (
        query_id,
        candidate_rank,
        case_title,
        document_id,
        chunk_id,
    ) = group_key

    group = group.copy()

    # --------------------------------------------------------
    # SORT BY SHAP CONTRIBUTION
    # --------------------------------------------------------

    group["abs_shap"] = (
        group["shap_value"].abs()
    )

    positive = (
        group[group["shap_value"] > 0]
        .sort_values(
            "shap_value",
            ascending=False
        )
    )

    negative = (
        group[group["shap_value"] < 0]
        .sort_values(
            "shap_value",
            ascending=True
        )
    )


    # --------------------------------------------------------
    # POSITIVE FACTORS
    # --------------------------------------------------------

    positive_factors = []

    for _, row in positive.head(5).iterrows():

        positive_factors.append({
            "feature": row["feature"],
            "feature_name": row["feature_name"],
            "feature_value": float(
                row["feature_value"]
            ),
            "shap_contribution": float(
                row["shap_value"]
            ),
            "explanation": row["explanation"],
        })


    # --------------------------------------------------------
    # NEGATIVE FACTORS
    # --------------------------------------------------------

    negative_factors = []

    for _, row in negative.head(5).iterrows():

        negative_factors.append({
            "feature": row["feature"],
            "feature_name": row["feature_name"],
            "feature_value": float(
                row["feature_value"]
            ),
            "shap_contribution": float(
                row["shap_value"]
            ),
            "explanation": row["explanation"],
        })


    # --------------------------------------------------------
    # ALL CONTRIBUTIONS
    # --------------------------------------------------------

    all_features = []

    for _, row in (
        group
        .sort_values(
            "abs_shap",
            ascending=False
        )
        .iterrows()
    ):

        all_features.append({
            "feature": row["feature"],
            "feature_name": row["feature_name"],
            "feature_value": float(
                row["feature_value"]
            ),
            "shap_contribution": float(
                row["shap_value"]
            ),
            "direction": row["direction"],
        })


    # --------------------------------------------------------
    # BUILD CANDIDATE OBJECT
    # --------------------------------------------------------

    first = group.iloc[0]

    candidate = {
        "query_id": int(query_id),
        "query": first["query"],
        "candidate_rank": int(candidate_rank),

        "case_title": case_title,
        "document_id": document_id,
        "chunk_id": chunk_id,

        "actual_relevance": int(
            first["relevance"]
        ),

        "positive_factors": positive_factors,
        "negative_factors": negative_factors,

        "all_feature_contributions": all_features,
    }

    results.append(candidate)


# ============================================================
# SORT RESULTS
# ============================================================

results.sort(
    key=lambda x: (
        x["query_id"],
        x["candidate_rank"],
    )
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# DISPLAY
# ============================================================

print("\n" + "=" * 70)
print("CANDIDATE-LEVEL EXPLANATION EXAMPLE")
print("=" * 70)


example = results[0]

print(
    json.dumps(
        example,
        indent=2,
        ensure_ascii=False
    )
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)

print(
    f"\nCandidates processed: {len(results)}"
)

print(
    f"Output: {OUTPUT_PATH}"
)
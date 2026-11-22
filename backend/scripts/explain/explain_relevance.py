from pathlib import Path

import joblib
import pandas as pd
import shap


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = Path(
    "eval/relevance_dataset_labeled.csv"
)

MODEL_PATH = Path(
    "ranking/models/relevance_model.pkl"
)

OUTPUT_PATH = Path(
    "eval/shap_explanations.csv"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "dense_score",
    "dense_rank",
    "bm25_score",
    "bm25_rank",
    "rrf_score",
    "keyword_overlap",
    "query_term_coverage",
    "article_overlap",
    "section_overlap",
    "legal_reference_overlap",
]


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("SHAP RELEVANCE EXPLAINABILITY")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Rows loaded: {len(df)}")


# ============================================================
# PREPARE FEATURES
# ============================================================

print("\nPreparing features...")

for feature in FEATURES:
    df[feature] = pd.to_numeric(
        df[feature],
        errors="coerce"
    )

    df[feature] = df[feature].fillna(0)


X = df[FEATURES]


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

print("\nLoading relevance model...")

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]

print("Model loaded successfully.")


# ============================================================
# CREATE SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP TreeExplainer...")

explainer = shap.TreeExplainer(model)

print("Calculating SHAP values...")

shap_values = explainer.shap_values(X)

print("SHAP values calculated.")


# ============================================================
# EXTRACT CLASS-1 SHAP VALUES
# ============================================================

if isinstance(shap_values, list):

    # Older SHAP versions
    #
    # shap_values[0] = class 0
    # shap_values[1] = class 1 / relevant

    if len(shap_values) == 2:
        relevant_shap = shap_values[1]
    else:
        relevant_shap = shap_values[0]

else:

    # Newer SHAP versions

    if len(shap_values.shape) == 3:
        relevant_shap = shap_values[:, :, 1]

    else:
        relevant_shap = shap_values


print(
    f"SHAP matrix shape: {relevant_shap.shape}"
)


# ============================================================
# CREATE EXPLANATION DATASET
# ============================================================

print("\nBuilding explanation dataset...")

rows = []

for i in range(len(df)):

    original_row = df.iloc[i]

    for feature_index, feature in enumerate(FEATURES):

        shap_value = float(
            relevant_shap[i][feature_index]
        )

        if shap_value > 0:
            direction = "supports relevance"
        elif shap_value < 0:
            direction = "opposes relevance"
        else:
            direction = "neutral"

        rows.append({
            "query_id": original_row["query_id"],
            "query": original_row["query"],
            "candidate_rank": original_row["candidate_rank"],
            "case_title": original_row["case_title"],
            "document_id": original_row["document_id"],
            "chunk_id": original_row["chunk_id"],
            "feature": feature,
            "feature_value": original_row[feature],
            "shap_value": shap_value,
            "direction": direction,
            "relevance": original_row["relevance"],
        })


explanation_df = pd.DataFrame(rows)


# ============================================================
# SAVE
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

explanation_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# DISPLAY EXAMPLES
# ============================================================

print("\n" + "=" * 70)
print("EXAMPLE SHAP EXPLANATIONS")
print("=" * 70)


# Show first 3 candidates from different queries

shown = 0
seen_candidates = set()

for _, row in df.iterrows():

    candidate_key = (
        row["query_id"],
        row["candidate_rank"]
    )

    if candidate_key in seen_candidates:
        continue

    seen_candidates.add(candidate_key)

    query_id = row["query_id"]
    case_title = row["case_title"]
    candidate_rank = row["candidate_rank"]

    candidate_explanation = explanation_df[
        (explanation_df["query_id"] == query_id)
        &
        (
            explanation_df["candidate_rank"]
            == candidate_rank
        )
    ].copy()

    candidate_explanation["abs_shap"] = (
        candidate_explanation["shap_value"].abs()
    )

    candidate_explanation = (
        candidate_explanation
        .sort_values(
            "abs_shap",
            ascending=False
        )
        .head(5)
    )

    print("\n" + "-" * 70)

    print(f"Query ID : {query_id}")
    print(f"Query    : {row['query']}")
    print(f"Case     : {case_title}")
    print(f"Rank     : {candidate_rank}")
    print(
        f"Actual relevance: "
        f"{int(row['relevance'])}"
    )

    print("\nTop contributing features:")

    for _, feature_row in candidate_explanation.iterrows():

        shap_value = feature_row["shap_value"]

        if shap_value > 0:
            sign = "+"
        else:
            sign = ""

        print(
            f"  "
            f"{feature_row['feature']:<30}"
            f"{sign}{shap_value:.4f}"
            f"  ({feature_row['direction']})"
        )

    shown += 1

    if shown >= 3:
        break


# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL SHAP FEATURE IMPORTANCE")
print("=" * 70)

global_importance = []

for feature_index, feature in enumerate(FEATURES):

    mean_abs_shap = abs(
        relevant_shap[:, feature_index]
    ).mean()

    global_importance.append({
        "feature": feature,
        "mean_abs_shap": mean_abs_shap,
    })


global_importance_df = pd.DataFrame(
    global_importance
).sort_values(
    "mean_abs_shap",
    ascending=False
)


for _, row in global_importance_df.iterrows():

    print(
        f"{row['feature']:<30}"
        f"{row['mean_abs_shap']:.6f}"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("SHAP EXPLANABILITY COMPLETE")
print("=" * 70)

print(f"\nSaved explanations:")
print(OUTPUT_PATH)

print(
    f"\nTotal explanation rows: "
    f"{len(explanation_df)}"
)
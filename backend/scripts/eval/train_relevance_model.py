from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = Path("eval/relevance_dataset_labeled.csv")

MODEL_DIR = Path("ranking/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "relevance_model.pkl"


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
# LOAD DATA
# ============================================================

print("=" * 70)
print("TRAINING LEGAL RELEVANCE MODEL")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Rows: {len(df)}")
print(f"Queries: {df['query_id'].nunique()}")


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

print("\nHandling missing values...")

for feature in FEATURES:
    df[feature] = pd.to_numeric(df[feature], errors="coerce")

    # Missing retrieval features mean the candidate was not
    # retrieved by that method.
    df[feature] = df[feature].fillna(0)


# ============================================================
# TRAIN / TEST SPLIT BY QUERY
# ============================================================

TRAIN_QUERY_IDS = list(range(1, 17))
TEST_QUERY_IDS = list(range(17, 21))

train_df = df[df["query_id"].isin(TRAIN_QUERY_IDS)].copy()
test_df = df[df["query_id"].isin(TEST_QUERY_IDS)].copy()

print("\nQuery split:")
print(f"Training queries: {TRAIN_QUERY_IDS}")
print(f"Testing queries : {TEST_QUERY_IDS}")

print("\nDataset split:")
print(f"Training rows: {len(train_df)}")
print(f"Testing rows : {len(test_df)}")


# ============================================================
# FEATURES / TARGET
# ============================================================

X_train = train_df[FEATURES]
y_train = train_df["relevance"].astype(int)

X_test = test_df[FEATURES]
y_test = test_df["relevance"].astype(int)


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

print("\nTraining labels:")
print(y_train.value_counts().sort_index())

print("\nTesting labels:")
print(y_test.value_counts().sort_index())


# ============================================================
# TRAIN RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=6,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(X_test)

y_prob = model.predict_proba(X_test)[:, 1]


# ============================================================
# EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0,
)

print(f"\nAccuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

if len(set(y_test)) == 2:
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC  : {auc:.4f}")


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0,
    )
)


print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

importance_df = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_,
})

importance_df = importance_df.sort_values(
    "importance",
    ascending=False,
)

for _, row in importance_df.iterrows():
    print(
        f"{row['feature']:<30} "
        f"{row['importance']:.4f}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
    },
    MODEL_PATH,
)

print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(f"Path: {MODEL_PATH}")
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = Path(
    "eval/shap_explanations.csv"
)

OUTPUT_PATH = Path(
    "eval/retrieval_explanations.csv"
)


# ============================================================
# FEATURE DISPLAY NAMES
# ============================================================

FEATURE_NAMES = {
    "rrf_score": "Hybrid RRF Score",
    "bm25_score": "BM25 Score",
    "dense_score": "Dense Similarity",
    "bm25_rank": "BM25 Rank",
    "dense_rank": "Dense Rank",
    "query_term_coverage": "Query Term Coverage",
    "keyword_overlap": "Keyword Overlap",
    "legal_reference_overlap": "Legal Reference Overlap",
    "article_overlap": "Article Overlap",
    "section_overlap": "Section Overlap",
}


# ============================================================
# EXPLANATION TEMPLATES
# ============================================================

def explain_feature(feature, value, shap_value):
    """
    Convert a feature + SHAP contribution into
    a human-readable explanation.
    """

    direction = "positive" if shap_value > 0 else "negative"

    if feature == "rrf_score":

        if direction == "positive":
            return (
                "The judgment received a strong hybrid retrieval "
                "score from the combined retrieval methods."
            )

        return (
            "The hybrid retrieval score contributed negatively "
            "to the relevance prediction."
        )


    if feature == "bm25_score":

        if direction == "positive":
            return (
                "The judgment has strong lexical overlap with "
                "the query."
            )

        return (
            "The lexical match with the query was relatively "
            "weak."
        )


    if feature == "dense_score":

        if direction == "positive":
            return (
                "The judgment has strong semantic similarity "
                "to the query."
            )

        return (
            "The semantic similarity between the query and "
            "judgment was relatively weak."
        )


    if feature == "bm25_rank":

        if direction == "positive":
            return (
                "The judgment received a favorable ranking "
                "from BM25 retrieval."
            )

        return (
            "The BM25 ranking did not strongly support "
            "the relevance prediction."
        )


    if feature == "dense_rank":

        if direction == "positive":
            return (
                "The judgment received a favorable ranking "
                "from dense semantic retrieval."
            )

        return (
            "The dense retrieval ranking provided weaker "
            "support for relevance."
        )


    if feature == "query_term_coverage":

        if direction == "positive":
            return (
                "A substantial portion of the important query "
                "terms is represented in the judgment evidence."
            )

        return (
            "The judgment evidence contains limited coverage "
            "of the important query terms."
        )


    if feature == "keyword_overlap":

        if direction == "positive":
            return (
                "Important keywords from the query overlap "
                "with the judgment evidence."
            )

        return (
            "There is limited keyword overlap between the "
            "query and judgment evidence."
        )


    if feature == "legal_reference_overlap":

        if direction == "positive":
            return (
                "The query and judgment share relevant legal "
                "references."
            )

        return (
            "The legal references in the query and judgment "
            "provide limited overlap."
        )


    if feature == "article_overlap":

        if direction == "positive":
            return (
                "The query and judgment contain matching "
                "constitutional Article references."
            )

        return (
            "The judgment does not contain a strong matching "
            "constitutional Article reference."
        )


    if feature == "section_overlap":

        if direction == "positive":
            return (
                "The query and judgment contain matching "
                "legal section references."
            )

        return (
            "The query and judgment do not have strong "
            "matching section references."
        )


    return (
        f"The {feature} feature contributed "
        f"{direction}ly to the relevance prediction."
    )


# ============================================================
# LOAD SHAP DATA
# ============================================================

print("=" * 70)
print("BUILDING HUMAN-READABLE RETRIEVAL EXPLANATIONS")
print("=" * 70)

print("\nLoading SHAP explanations...")

df = pd.read_csv(INPUT_PATH)

print(f"Rows loaded: {len(df)}")


# ============================================================
# CLEAN DATA
# ============================================================

df["shap_value"] = pd.to_numeric(
    df["shap_value"],
    errors="coerce"
).fillna(0)

df["feature_value"] = pd.to_numeric(
    df["feature_value"],
    errors="coerce"
).fillna(0)


# ============================================================
# BUILD EXPLANATION ROWS
# ============================================================

print("\nGenerating human-readable explanations...")

rows = []

for _, row in df.iterrows():

    shap_value = float(row["shap_value"])

    # Ignore completely neutral features.
    if abs(shap_value) < 1e-9:
        continue

    feature = row["feature"]

    rows.append({
        "query_id": row["query_id"],
        "query": row["query"],
        "candidate_rank": row["candidate_rank"],
        "case_title": row["case_title"],
        "document_id": row["document_id"],
        "chunk_id": row["chunk_id"],
        "feature": feature,
        "feature_name": FEATURE_NAMES.get(
            feature,
            feature
        ),
        "feature_value": row["feature_value"],
        "shap_value": shap_value,
        "direction": (
            "positive"
            if shap_value > 0
            else "negative"
        ),
        "explanation": explain_feature(
            feature,
            row["feature_value"],
            shap_value
        ),
        "relevance": row["relevance"],
    })


explanation_df = pd.DataFrame(rows)


# ============================================================
# SAVE FEATURE-LEVEL EXPLANATIONS
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
print("EXAMPLE HUMAN-READABLE EXPLANATIONS")
print("=" * 70)


shown = 0
seen = set()

for _, row in explanation_df.iterrows():

    key = (
        row["query_id"],
        row["candidate_rank"]
    )

    if key in seen:
        continue

    seen.add(key)

    candidate = explanation_df[
        (explanation_df["query_id"] == row["query_id"])
        &
        (
            explanation_df["candidate_rank"]
            == row["candidate_rank"]
        )
    ].copy()

    # Strongest contributions first.
    candidate["abs_shap"] = (
        candidate["shap_value"].abs()
    )

    candidate = candidate.sort_values(
        "abs_shap",
        ascending=False
    )

    print("\n" + "-" * 70)

    print(f"Query ID : {row['query_id']}")
    print(f"Query    : {row['query']}")
    print(f"Case     : {row['case_title']}")
    print(f"Rank     : {row['candidate_rank']}")
    print(
        f"Relevance: {int(row['relevance'])}"
    )

    print("\nWhy this result was suggested:")

    for _, feature_row in candidate.head(5).iterrows():

        sign = (
            "+"
            if feature_row["shap_value"] > 0
            else ""
        )

        print(
            f"  {feature_row['feature_name']}"
            f" ({sign}{feature_row['shap_value']:.4f})"
        )

        print(
            f"      {feature_row['explanation']}"
        )

    shown += 1

    if shown >= 5:
        break


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("EXPLANATION BUILD COMPLETE")
print("=" * 70)

print(
    f"\nFeature-level explanations saved to:"
)

print(OUTPUT_PATH)

print(
    f"\nExplanation rows generated: "
    f"{len(explanation_df)}"
)
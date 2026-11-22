from pathlib import Path

import joblib
import pandas as pd
import shap


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = Path(
    "ranking/models/relevance_model.pkl"
)


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
# HUMAN-READABLE EXPLANATIONS
# ============================================================

def explain_feature(feature, shap_value):
    """
    Generate a scientifically safer explanation.

    Important:
    We describe what the SHAP contribution means.
    We do NOT infer that the raw feature value itself
    is high or low unless we explicitly establish a threshold.
    """

    if shap_value > 0:

        if feature == "rrf_score":
            return (
                "The hybrid RRF score contributed positively "
                "to the relevance prediction."
            )

        if feature == "bm25_score":
            return (
                "The BM25 score contributed positively "
                "to the relevance prediction."
            )

        if feature == "dense_score":
            return (
                "The dense semantic similarity contributed "
                "positively to the relevance prediction."
            )

        if feature == "bm25_rank":
            return (
                "The BM25 ranking contributed positively "
                "to the relevance prediction."
            )

        if feature == "dense_rank":
            return (
                "The dense retrieval ranking contributed "
                "positively to the relevance prediction."
            )

        if feature == "query_term_coverage":
            return (
                "Query-term coverage contributed positively "
                "to the relevance prediction."
            )

        if feature == "keyword_overlap":
            return (
                "Keyword overlap contributed positively "
                "to the relevance prediction."
            )

        if feature == "legal_reference_overlap":
            return (
                "Overlap in legal references contributed "
                "positively to the relevance prediction."
            )

        if feature == "article_overlap":
            return (
                "Matching constitutional Article references "
                "contributed positively to the relevance prediction."
            )

        if feature == "section_overlap":
            return (
                "Matching legal section references contributed "
                "positively to the relevance prediction."
            )


    elif shap_value < 0:

        if feature == "rrf_score":
            return (
                "The hybrid RRF score contributed negatively "
                "to the relevance prediction."
            )

        if feature == "bm25_score":
            return (
                "The BM25 score contributed negatively "
                "to the relevance prediction."
            )

        if feature == "dense_score":
            return (
                "The dense semantic similarity contributed "
                "negatively to the relevance prediction."
            )

        if feature == "bm25_rank":
            return (
                "The BM25 ranking contributed negatively "
                "to the relevance prediction."
            )

        if feature == "dense_rank":
            return (
                "The dense retrieval ranking contributed "
                "negatively to the relevance prediction."
            )

        if feature == "query_term_coverage":
            return (
                "Query-term coverage contributed negatively "
                "to the relevance prediction."
            )

        if feature == "keyword_overlap":
            return (
                "Keyword overlap contributed negatively "
                "to the relevance prediction."
            )

        if feature == "legal_reference_overlap":
            return (
                "Overlap in legal references contributed "
                "negatively to the relevance prediction."
            )

        if feature == "article_overlap":
            return (
                "Matching constitutional Article references "
                "contributed negatively to the relevance prediction."
            )

        if feature == "section_overlap":
            return (
                "Matching legal section references contributed "
                "negatively to the relevance prediction."
            )


    return (
        "This feature had no meaningful contribution "
        "to the relevance prediction."
    )


# ============================================================
# EXPLANATION ENGINE
# ============================================================

class RetrievalExplanationEngine:

    def __init__(self, model_path=MODEL_PATH):

        print("Loading relevance model...")

        model_data = joblib.load(model_path)

        self.model = model_data["model"]

        self.features = model_data.get(
            "features",
            FEATURES
        )

        print("Creating SHAP TreeExplainer...")

        self.explainer = shap.TreeExplainer(
            self.model
        )

        print("Explanation engine ready.")


    # ========================================================
    # PREPARE FEATURES
    # ========================================================

    def _prepare_features(self, candidate):

        values = {}

        for feature in self.features:

            value = candidate.get(
                feature,
                0
            )

            if value is None:
                value = 0

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0

            values[feature] = value

        return pd.DataFrame(
            [values],
            columns=self.features
        )


    # ========================================================
    # CALCULATE SHAP
    # ========================================================

    def _calculate_shap(self, X):

        shap_values = self.explainer.shap_values(X)

        # Older SHAP versions
        if isinstance(shap_values, list):

            if len(shap_values) == 2:

                return shap_values[1][0]

            return shap_values[0][0]


        # Newer SHAP versions
        if len(shap_values.shape) == 3:

            return shap_values[0, :, 1]


        return shap_values[0]


    # ========================================================
    # EXPLAIN ONE CANDIDATE
    # ========================================================

    def explain_candidate(self, candidate):

        X = self._prepare_features(
            candidate
        )

        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        probability = float(
            self.model.predict_proba(X)[0][1]
        )

        prediction = int(
            self.model.predict(X)[0]
        )


        # ----------------------------------------------------
        # SHAP VALUES
        # ----------------------------------------------------

        shap_values = self._calculate_shap(X)


        # ----------------------------------------------------
        # BUILD CONTRIBUTIONS
        # ----------------------------------------------------

        contributions = []

        for index, feature in enumerate(
            self.features
        ):

            shap_value = float(
                shap_values[index]
            )

            feature_value = float(
                X.iloc[0][feature]
            )

            contributions.append({

                "feature": feature,

                "feature_name": FEATURE_NAMES.get(
                    feature,
                    feature
                ),

                "feature_value": feature_value,

                "shap_contribution": shap_value,

                "direction": (
                    "positive"
                    if shap_value > 0
                    else (
                        "negative"
                        if shap_value < 0
                        else "neutral"
                    )
                ),

                "explanation": explain_feature(
                    feature,
                    shap_value
                )
            })


        # ----------------------------------------------------
        # SORT BY IMPORTANCE
        # ----------------------------------------------------

        contributions.sort(
            key=lambda x: abs(
                x["shap_contribution"]
            ),
            reverse=True
        )


        # ----------------------------------------------------
        # POSITIVE / NEGATIVE
        # ----------------------------------------------------

        positive_factors = [
            item
            for item in contributions
            if item["shap_contribution"] > 0
        ][:5]


        negative_factors = [
            item
            for item in contributions
            if item["shap_contribution"] < 0
        ][:5]


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "relevance_probability": float(probability),
            "prediction": int(prediction),
            "relevance_prediction": int(prediction),

            "feature_values": {
                feature: float(X.iloc[0][feature])
                for feature in FEATURE_NAMES
            },

            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 70
    )

    print(
        "TESTING RETRIEVAL EXPLANATION ENGINE"
    )

    print(
        "=" * 70
    )


    # Example candidate using the same
    # feature structure as the hybrid pipeline.

    candidate = {

        "dense_score": 0.765462339,

        "dense_rank": 7,

        "bm25_score": 28.04266774,

        "bm25_rank": 12,

        "rrf_score": 0.028814262,

        "keyword_overlap": 0.5,

        "query_term_coverage": 0.5,

        "article_overlap": 1.0,

        "section_overlap": 0,

        "legal_reference_overlap": 1.0,
    }


    engine = RetrievalExplanationEngine()


    explanation = engine.explain_candidate(
        candidate
    )


    print(
        "\nRelevance probability:",
        round(
            explanation[
                "relevance_probability"
            ],
            4
        )
    )


    print(
        "Prediction:",
        explanation[
            "relevance_prediction"
        ]
    )


    print(
        "\nPositive factors:"
    )

    for factor in explanation[
        "positive_factors"
    ]:

        print(
            f"  + "
            f"{factor['feature_name']}: "
            f"{factor['shap_contribution']:.4f}"
        )

        print(
            f"    {factor['explanation']}"
        )


    print(
        "\nNegative factors:"
    )

    for factor in explanation[
        "negative_factors"
    ]:

        print(
            f"  "
            f"{factor['feature_name']}: "
            f"{factor['shap_contribution']:.4f}"
        )

        print(
            f"    {factor['explanation']}"
        )


    print(
        "\n"
        + "=" * 70
    )

    print(
        "TEST COMPLETE"
    )

    print(
        "=" * 70
    )
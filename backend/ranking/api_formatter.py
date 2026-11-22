def build_api_result(
    rank,
    result,
    explanation,
):
    chunk = result.get("chunk", {})

    positive_factors = []

    for factor in explanation.get(
        "positive_factors",
        []
    ):
        positive_factors.append({
            "feature": factor.get(
                "feature_name"
            ),

            "contribution": round(
                float(
                    factor.get(
                        "shap_contribution",
                        0.0
                    )
                ),
                4,
            ),

            "explanation": factor.get(
                "explanation",
                ""
            ),
        })

    negative_factors = []

    for factor in explanation.get(
        "negative_factors",
        []
    ):
        negative_factors.append({
            "feature": factor.get(
                "feature_name"
            ),

            "contribution": round(
                float(
                    factor.get(
                        "shap_contribution",
                        0.0
                    )
                ),
                4,
            ),

            "explanation": factor.get(
                "explanation",
                ""
            ),
        })

    feature_values = {}

    for feature, value in explanation.get(
        "feature_values",
        {}
    ).items():

        if value is None:
            feature_values[feature] = None
        else:
            feature_values[feature] = round(
                float(value),
                4,
            )

    return {

        # -------------------------------------------------
        # Result ranking
        # -------------------------------------------------

        "rank": rank,

        # -------------------------------------------------
        # Case information
        # -------------------------------------------------

        "case": {
            "title": chunk.get(
                "case_title"
            ),

            "date": chunk.get(
                "date"
            ),

            "citation": chunk.get(
                "citation"
            ),

            "bench": chunk.get(
                "bench"
            ),

            "petitioner": chunk.get(
                "petitioner"
            ),

            "respondent": chunk.get(
                "respondent"
            ),
        },

        # -------------------------------------------------
        # Retrieval signals
        # -------------------------------------------------

        "retrieval": {

            "rrf_score": round(
                float(
                    result.get(
                        "rrf_score",
                        0.0
                    )
                ),
                6,
            ),

            "dense_score": (
                round(
                    float(
                        result["dense_score"]
                    ),
                    6,
                )
                if result.get(
                    "dense_score"
                ) is not None
                else None
            ),

            "dense_rank": result.get(
                "dense_rank"
            ),

            "bm25_score": (
                round(
                    float(
                        result["bm25_score"]
                    ),
                    6,
                )
                if result.get(
                    "bm25_score"
                ) is not None
                else None
            ),

            "bm25_rank": result.get(
                "bm25_rank"
            ),
        },

        # -------------------------------------------------
        # Relevance model
        # -------------------------------------------------

        "relevance": {

            "model_score": round(
                float(
                    explanation.get(
                        "relevance_probability",
                        0.0
                    )
                ),
                4,
            ),

            "prediction": int(
                explanation.get(
                    "prediction",
                    0
                )
            ),
        },

        # -------------------------------------------------
        # XAI explanation
        # -------------------------------------------------

        "explanation": {

            "positive_factors":
                positive_factors,

            "negative_factors":
                negative_factors,

            "feature_values":
                feature_values,
        },

        # -------------------------------------------------
        # Evidence
        # -------------------------------------------------

        "evidence": chunk.get(
            "text",
            ""
        ),
    }
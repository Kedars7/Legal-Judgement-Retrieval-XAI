from pathlib import Path
import sys

# Allow imports from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ranking.api_formatter import build_api_result
from ranking.feature_extractor import extract_features
from ranking.explanation_engine import RetrievalExplanationEngine

# Import the existing retrieval functions
from scripts.testing.search_hybrid import (
    load_model,
    load_faiss,
    load_metadata,
    load_bm25,
    validate_mapping,
    # create_query_embedding,
    dense_search,
    bm25_search,
    hybrid_rrf,
    diversify_by_judgment,
)


class LegalSearchService:

    def __init__(self):

        print("Initializing Legal Search Service...")

        # -------------------------------------------------
        # Load ML / Retrieval components
        # -------------------------------------------------

        self.tokenizer, self.model = load_model()

        self.index = load_faiss()

        self.metadata = load_metadata()

        self.bm25, self.bm25_metadata = load_bm25()

        # -------------------------------------------------
        # Validate mapping
        # -------------------------------------------------

        validate_mapping(
            self.index,
            self.metadata,
            self.bm25,
            self.bm25_metadata,
        )

        # -------------------------------------------------
        # Load XAI engine
        # -------------------------------------------------

        self.explanation_engine = (
            RetrievalExplanationEngine()
        )

        print(
            "Legal Search Service ready."
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    def search(
        self,
        query,
        top_k=10,
    ):

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query = query.strip()

        # -------------------------------------------------
        # 1. Dense retrieval
        # -------------------------------------------------

        dense_results = dense_search(
            query,
            self.index,
            self.metadata,
            self.tokenizer,
            self.model,
        )

        # -------------------------------------------------
        # 2. BM25 retrieval
        # -------------------------------------------------

        bm25_results = bm25_search(
            query,
            self.bm25,
            self.bm25_metadata,
        )

        # -------------------------------------------------
        # 3. Hybrid RRF
        # -------------------------------------------------

        hybrid_results = hybrid_rrf(
            dense_results,
            bm25_results,
        )

        # -------------------------------------------------
        # 4. Diversification
        # -------------------------------------------------

        final_results = diversify_by_judgment(
            hybrid_results,
            self.metadata,
        )

        # -------------------------------------------------
        # 5. Take top K
        # -------------------------------------------------

        final_results = final_results[:top_k]

        formatted_results = []

        # -------------------------------------------------
        # 6. Feature extraction + SHAP explanation
        # -------------------------------------------------

        for rank, result in enumerate(
            final_results,
            start=1,
        ):

            features = extract_features(
                query,
                result,
            )

            explanation = (
                self.explanation_engine
                .explain_candidate(
                    features
                )
            )

            result["explanation"] = (
                explanation
            )

            # -------------------------------------------------
            # 7. Convert to API-ready JSON
            # -------------------------------------------------

            api_result = build_api_result(
                rank=rank,
                result=result,
                explanation=explanation,
            )

            formatted_results.append(
                api_result
            )

        # -------------------------------------------------
        # 8. Final response
        # -------------------------------------------------

        return {
            "query": query,

            "retrieval": {
                "dense_top_k": 50,
                "bm25_top_k": 50,
                "max_chunks_per_judgment": 2,
                "rrf_constant": 60,
            },

            "results": formatted_results,

            "total_results": len(
                formatted_results
            ),
        }


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    service = LegalSearchService()

    query = (
        "Whether the accused is entitled "
        "to protection under Article 14 "
        "of the Constitution"
    )

    response = service.search(
        query,
        top_k=3,
    )

    import json

    print("\n")
    print("=" * 80)
    print("API RESPONSE")
    print("=" * 80)

    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False,
        )
    )
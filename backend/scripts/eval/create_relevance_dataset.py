import csv
import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ============================================================
# IMPORT EXISTING HYBRID RETRIEVAL FUNCTIONS
# ============================================================

from scripts.testing.search_hybrid import (
    load_model,
    load_faiss,
    load_metadata,
    load_bm25,
    validate_mapping,
    dense_search,
    bm25_search,
    hybrid_rrf,
    diversify_by_judgment,
)

from ranking.feature_extractor import extract_features


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_PATH = (
    PROJECT_ROOT
    / "eval"
    / "relevance_dataset.csv"
)


# ============================================================
# V1 QUERY SET
# ============================================================

QUERIES = [

    "Whether the accused is entitled to protection under Article 14 of the Constitution",

    "Whether a law violates the fundamental right to equality under Article 14",

    "Whether preventive detention violates fundamental rights under the Constitution",

    "Whether the petitioner can challenge an election result through a writ petition",

    "Whether the High Court has jurisdiction to interfere with an election process",

    "Whether a tax liability can be imposed retrospectively",

    "Whether income received by a company is taxable under the applicable law",

    "Whether a government order violates the fundamental rights of a citizen",

    "Whether the accused can challenge the validity of a criminal conviction",

    "Whether a statute is inconsistent with the Constitution",

    "Whether the State can restrict a fundamental right",

    "Whether detention is valid under the procedure established by law",

    "Whether the right to personal liberty is protected by the Constitution",

    "Whether a classification made by law is constitutionally valid",

    "Whether a statutory provision violates Article 19 of the Constitution",

    "Whether a statutory provision violates Article 21 of the Constitution",

    "Whether a person has a right to approach the Supreme Court under Article 32",

    "Whether a High Court can issue a writ under Article 226",

    "Whether the government can impose restrictions in the interest of public order",

    "Whether the legislation is protected from challenge under the Constitution",
]


# ============================================================
# CSV VALUE HELPER
# ============================================================

def csv_value(value):

    if value is None:
        return ""

    if isinstance(value, list):
        return "; ".join(
            str(item)
            for item in value
        )

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("CREATING RELEVANCE DATASET")
    print("=" * 80)

    print()
    print(f"Queries : {len(QUERIES)}")
    print(f"Output  : {OUTPUT_PATH}")

    # ========================================================
    # LOAD EXISTING RETRIEVAL RESOURCES
    # ========================================================

    print()
    print("Loading existing hybrid retrieval resources...")

    tokenizer, model = load_model()

    print()

    faiss_index = load_faiss()

    print()

    metadata = load_metadata()

    print()

    bm25, bm25_metadata = load_bm25()

    print()

    # ========================================================
    # VALIDATE MAPPING
    # ========================================================

    validate_mapping(
        faiss_index,
        metadata,
        bm25,
        bm25_metadata
    )

    # ========================================================
    # COLLECT DATASET ROWS
    # ========================================================

    rows = []

    # ========================================================
    # PROCESS EACH QUERY
    # ========================================================

    for query_id, query in enumerate(
        QUERIES,
        start=1
    ):

        print()
        print("-" * 80)
        print(
            f"QUERY {query_id}/{len(QUERIES)}"
        )
        print(query)

        # ----------------------------------------------------
        # Dense retrieval
        # ----------------------------------------------------

        dense_results = dense_search(
            query,
            faiss_index,
            metadata,
            tokenizer,
            model
        )

        # ----------------------------------------------------
        # BM25 retrieval
        # ----------------------------------------------------

        bm25_results = bm25_search(
            query,
            bm25,
            bm25_metadata
        )

        # ----------------------------------------------------
        # RRF
        # ----------------------------------------------------

        hybrid_candidates = hybrid_rrf(
            dense_results,
            bm25_results
        )

        # ----------------------------------------------------
        # Diversification
        # ----------------------------------------------------

        final_results = diversify_by_judgment(
            hybrid_candidates,
            metadata
        )

        # ----------------------------------------------------
        # Only top 10 candidates
        # ----------------------------------------------------

        final_results = final_results[:10]

        print(
            f"Candidates collected: "
            f"{len(final_results)}"
        )

        # ====================================================
        # EXTRACT FEATURES
        # ====================================================

        for candidate_rank, result in enumerate(
            final_results,
            start=1
        ):

            features = extract_features(
                query,
                result
            )

            chunk = result["chunk"]

            row = {

                "query_id": query_id,

                "query": query,

                "candidate_rank": candidate_rank,

                "case_title": chunk.get(
                    "case_title",
                    ""
                ),

                "document_id": chunk.get(
                    "document_id",
                    ""
                ),

                "chunk_id": chunk.get(
                    "chunk_id",
                    ""
                ),

                # Retrieval features
                "dense_score": features.get(
                    "dense_score"
                ),

                "dense_rank": features.get(
                    "dense_rank"
                ),

                "bm25_score": features.get(
                    "bm25_score"
                ),

                "bm25_rank": features.get(
                    "bm25_rank"
                ),

                "rrf_score": features.get(
                    "rrf_score"
                ),

                # Text features
                "keyword_overlap": features.get(
                    "keyword_overlap"
                ),

                "query_term_coverage": features.get(
                    "query_term_coverage"
                ),

                # Legal features
                "article_overlap": features.get(
                    "article_overlap"
                ),

                "section_overlap": features.get(
                    "section_overlap"
                ),

                "legal_reference_overlap": features.get(
                    "legal_reference_overlap"
                ),

                # Evidence
                "matched_keywords": features.get(
                    "matched_keywords"
                ),

                "matched_articles": features.get(
                    "matched_articles"
                ),

                "matched_sections": features.get(
                    "matched_sections"
                ),

                "matched_legal_references": features.get(
                    "matched_legal_references"
                ),

                # ------------------------------------------------
                # MANUAL LABEL
                # ------------------------------------------------
                #
                # Leave empty for now.
                #
                "relevance": ""
            }

            rows.append(row)

    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # CSV COLUMNS
    # ========================================================

    fieldnames = [

        "query_id",

        "query",

        "candidate_rank",

        "case_title",

        "document_id",

        "chunk_id",

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

        "matched_keywords",

        "matched_articles",

        "matched_sections",

        "matched_legal_references",

        "relevance",
    ]

    # ========================================================
    # WRITE CSV
    # ========================================================

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in rows:

            writer.writerow({
                key: csv_value(value)
                for key, value in row.items()
            })

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 80)
    print("DATASET CREATION COMPLETE")
    print("=" * 80)

    print(
        f"Total queries    : {len(QUERIES)}"
    )

    print(
        f"Total candidates : {len(rows)}"
    )

    print(
        f"Expected         : {len(QUERIES) * 10}"
    )

    print(
        f"Output           : {OUTPUT_PATH}"
    )

    print()
    print(
        "The 'relevance' column is intentionally empty."
    )

    print(
        "We will label it in the next step."
    )


if __name__ == "__main__":
    main()
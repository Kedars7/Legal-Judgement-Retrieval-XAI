import re
from collections import Counter


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "be", "been", "being", "of", "in", "on", "at",
    "to", "for", "from", "by", "with", "and",
    "or", "as", "that", "this", "these", "those",
    "it", "its", "has", "have", "had", "not",
    "but", "if", "then", "than", "which", "who",
    "whom", "what", "when", "where", "how",
    "whether", "under", "into", "about"
}


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def extract_legal_references(text):
    """
    Extract legal references such as:

    Article 14
    Article 21
    Article 14(1)
    Section 302
    Section 57
    """

    pattern = (
        r"\b(article|section)\s+"
        r"(\d+[a-z]?)"
        r"((?:\(\d+\))*)"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    articles = set()
    sections = set()

    for ref_type, number, subsections in matches:

        reference = f"{ref_type.lower()} {number}{subsections}"

        if ref_type.lower() == "article":
            articles.add(reference)
        else:
            sections.add(reference)

    return articles, sections


def extract_features(query, result):

    chunk = result["chunk"]
    document_text = chunk.get("text", "")

    # ---------------------------------------------------------
    # 1. Extract legal references first
    # ---------------------------------------------------------

    query_articles, query_sections = extract_legal_references(query)

    document_articles, document_sections = extract_legal_references(
        document_text
    )

    matched_articles = query_articles & document_articles
    matched_sections = query_sections & document_sections

    # ---------------------------------------------------------
    # 2. Legal reference overlap
    # ---------------------------------------------------------

    if query_articles:
        article_overlap = (
            len(matched_articles) / len(query_articles)
        )
    else:
        article_overlap = None

    if query_sections:
        section_overlap = (
            len(matched_sections) / len(query_sections)
        )
    else:
        section_overlap = None

    query_legal_references = query_articles | query_sections
    document_legal_references = (
        document_articles | document_sections
    )

    matched_legal_references = (
        query_legal_references &
        document_legal_references
    )

    if query_legal_references:
        legal_reference_overlap = (
            len(matched_legal_references)
            / len(query_legal_references)
        )
    else:
        legal_reference_overlap = None

    # ---------------------------------------------------------
    # 3. Remove legal-reference tokens from ordinary keywords
    # ---------------------------------------------------------

    query_without_references = query

    for article in query_articles:
        query_without_references = re.sub(
            re.escape(article),
            " ",
            query_without_references,
            flags=re.IGNORECASE
        )

    for section in query_sections:
        query_without_references = re.sub(
            re.escape(section),
            " ",
            query_without_references,
            flags=re.IGNORECASE
        )

    query_tokens = [
        token
        for token in tokenize(query_without_references)
        if token not in STOPWORDS
    ]

    document_tokens = tokenize(document_text)

    query_terms = set(query_tokens)
    document_terms = set(document_tokens)

    common_terms = query_terms & document_terms

    # ---------------------------------------------------------
    # 4. Normal keyword overlap
    # ---------------------------------------------------------

    keyword_overlap = (
        len(common_terms) / len(query_terms)
        if query_terms
        else 0.0
    )

    # ---------------------------------------------------------
    # 5. Query term coverage
    # ---------------------------------------------------------

    query_counts = Counter(query_tokens)
    document_counts = Counter(document_tokens)

    matched_occurrences = sum(
        min(
            query_counts[word],
            document_counts[word]
        )
        for word in query_counts
    )

    query_term_coverage = (
        matched_occurrences / len(query_tokens)
        if query_tokens
        else 0.0
    )

    # ---------------------------------------------------------
    # 6. Final feature dictionary
    # ---------------------------------------------------------

    features = {

        # Retrieval features
        "dense_score": result.get("dense_score"),
        "dense_rank": result.get("dense_rank"),

        "bm25_score": result.get("bm25_score"),
        "bm25_rank": result.get("bm25_rank"),

        "rrf_score": result.get("rrf_score"),

        # Text matching features
        "keyword_overlap": round(
            keyword_overlap,
            4
        ),

        "query_term_coverage": round(
            query_term_coverage,
            4
        ),

        # Legal-reference features
        "article_overlap": (
            round(article_overlap, 4)
            if article_overlap is not None
            else None
        ),

        "section_overlap": (
            round(section_overlap, 4)
            if section_overlap is not None
            else None
        ),

        "legal_reference_overlap": (
            round(
                legal_reference_overlap,
                4
            )
            if legal_reference_overlap is not None
            else None
        ),

        # Explainable matched evidence
        "matched_keywords": sorted(
            common_terms
        ),

        "matched_articles": sorted(
            matched_articles
        ),

        "matched_sections": sorted(
            matched_sections
        ),

        "matched_legal_references": sorted(
            matched_legal_references
        )
    }

    return features
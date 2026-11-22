import pickle
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BM25_INDEX_PATH = Path("index/bm25/bm25.pkl")

BM25_METADATA_PATH = Path("index/bm25/bm25_metadata.pkl")

TOP_K = 10


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    return re.findall(r"\b\w+\b", text.lower())


# ============================================================
# LOAD BM25
# ============================================================

def load_bm25():

    print("Loading BM25 index...")

    with open(BM25_INDEX_PATH, "rb") as f:

        bm25 = pickle.load(f)

    print("BM25 index loaded.")

    return bm25


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata():

    print("Loading BM25 metadata...")

    with open(BM25_METADATA_PATH, "rb") as f:

        metadata = pickle.load(f)

    print(f"Metadata records: {len(metadata)}")

    return metadata


# ============================================================
# SEARCH BM25
# ============================================================

def search(query, bm25, metadata):

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = scores.argsort()[::-1][:TOP_K]

    results = []

    for rank, index in enumerate(ranked_indices, start=1):

        chunk = metadata[index]

        results.append({

            "rank": rank,

            "score": float(scores[index]),

            "chunk": chunk,

            "text": chunk.get("text", "")

        })

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(query, results):

    print()
    print("=" * 80)
    print("BM25 SEARCH RESULTS")
    print("=" * 80)

    print(f"Query: {query}")
    print()

    for result in results:

        chunk = result["chunk"]

        print("-" * 80)

        print(f"Rank       : {result['rank']}")
        print(f"BM25 Score : {result['score']:.4f}")
        print(f"Chunk ID    : {chunk['chunk_id']}")
        print(f"Case       : {chunk['case_title']}")
        print(f"Date       : {chunk['date']}")
        print(f"Citation   : {chunk['citation']}")
        print(f"Chunk Index: {chunk['chunk_index']}")
        print(f"Words      : {chunk['word_count']}")

        print()

        text = result["text"]

        preview = text[:500].replace("\n", " ")

        print("Text       :", preview)

        if len(text) > 500:

            print("...")

        print()

    print("=" * 80)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("LEGAL JUDGMENT BM25 SEARCH - V1")
    print("=" * 80)

    bm25 = load_bm25()

    print()

    metadata = load_metadata()

    print()

    while True:

        query = input(
            "Enter legal query (type 'exit' to quit):\n> "
        ).strip()

        if query.lower() == "exit":

            print("Exiting.")

            break

        if not query:

            print("Please enter a query.")

            continue

        results = search(
            query,
            bm25,
            metadata
        )

        display_results(
            query,
            results
        )


if __name__ == "__main__":

    main()
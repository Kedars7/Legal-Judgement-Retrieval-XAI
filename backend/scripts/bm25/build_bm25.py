import json
import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


# ============================================================
# CONFIGURATION
# ============================================================

METADATA_PATH = Path("embeddings/baseline_100/metadata.jsonl")

OUTPUT_DIR = Path("index/bm25")

BM25_INDEX_PATH = OUTPUT_DIR / "bm25.pkl"
BM25_METADATA_PATH = OUTPUT_DIR / "bm25_metadata.pkl"


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Convert text into lowercase lexical tokens.
    """
    return re.findall(r"\b\w+\b", text.lower())


# ============================================================
# LOAD CURRENT V1 CHUNKS
# ============================================================

def load_chunks():

    print("Loading V1 chunk metadata...")

    metadata = []

    with open(METADATA_PATH, "r", encoding="utf-8") as f:

        for line in f:

            if line.strip():

                metadata.append(json.loads(line))

    print(f"Chunks loaded: {len(metadata)}")

    return metadata


# ============================================================
# BUILD BM25
# ============================================================

def build_bm25(metadata):

    print()
    print("Tokenizing chunks...")

    tokenized_chunks = []

    for i, chunk in enumerate(metadata):

        text = chunk.get("text", "")

        tokens = tokenize(text)

        tokenized_chunks.append(tokens)

        if (i + 1) % 500 == 0:
            print(f"Tokenized {i + 1}/{len(metadata)}")

    print()
    print("Building BM25 index...")

    bm25 = BM25Okapi(tokenized_chunks)

    return bm25


# ============================================================
# SAVE INDEX
# ============================================================

def save_index(bm25, metadata):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("Saving BM25 index...")

    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(bm25, f)

    with open(BM25_METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"BM25 index saved to: {BM25_INDEX_PATH}")
    print(f"BM25 metadata saved to: {BM25_METADATA_PATH}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("BUILDING BM25 LEGAL JUDGMENT INDEX - V1")
    print("=" * 80)

    metadata = load_chunks()

    if not metadata:

        print("ERROR: No chunks found.")

        return

    bm25 = build_bm25(metadata)

    save_index(bm25, metadata)

    print()
    print("=" * 80)
    print("BM25 BUILD COMPLETE")
    print("=" * 80)

    print(f"Total chunks indexed: {len(metadata)}")


if __name__ == "__main__":
    main()
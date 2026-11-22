import json
from pathlib import Path

import faiss
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDINGS_FILE = Path(
    "embeddings/baseline_100/embeddings.npy"
)

METADATA_FILE = Path(
    "embeddings/baseline_100/metadata.jsonl"
)

OUTPUT_DIR = Path(
    "index/baseline_100"
)

INDEX_FILE = OUTPUT_DIR / "legal_judgments.faiss"


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

print("=" * 60)
print("BUILDING FAISS INDEX")
print("=" * 60)

print(f"Embeddings : {EMBEDDINGS_FILE}")
print(f"Metadata   : {METADATA_FILE}")
print()

embeddings = np.load(
    EMBEDDINGS_FILE
).astype(
    np.float32
)

print(
    f"Embeddings shape: {embeddings.shape}"
)

# ------------------------------------------------------------
# Basic validation
# ------------------------------------------------------------

if embeddings.ndim != 2:
    raise ValueError(
        "Embeddings must be a 2D array."
    )

if np.isnan(embeddings).any():
    raise ValueError(
        "Embeddings contain NaN values."
    )

if np.isinf(embeddings).any():
    raise ValueError(
        "Embeddings contain Inf values."
    )


# ============================================================
# LOAD METADATA
# ============================================================

metadata = []

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if line:
            metadata.append(
                json.loads(line)
            )

print(
    f"Metadata records: {len(metadata)}"
)


# ============================================================
# ALIGNMENT CHECK
# ============================================================

if len(embeddings) != len(metadata):

    raise ValueError(
        f"Mismatch detected!\n"
        f"Embeddings: {len(embeddings)}\n"
        f"Metadata:   {len(metadata)}"
    )

print()
print("Embedding ↔ metadata alignment: OK")


# ============================================================
# CREATE FAISS INDEX
# ============================================================

dimension = embeddings.shape[1]

print(
    f"Vector dimension: {dimension}"
)

print(
    "Creating IndexFlatIP..."
)

index = faiss.IndexFlatIP(
    dimension
)


# ============================================================
# ADD VECTORS
# ============================================================

index.add(
    embeddings
)

print(
    f"Vectors in FAISS: {index.ntotal}"
)


# ============================================================
# SAVE INDEX
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

faiss.write_index(
    index,
    str(INDEX_FILE)
)


# ============================================================
# VALIDATION
# ============================================================

loaded_index = faiss.read_index(
    str(INDEX_FILE)
)

print()
print("=" * 60)
print("FAISS VALIDATION")
print("=" * 60)

print(
    f"Index type       : {type(loaded_index).__name__}"
)

print(
    f"Index dimension  : {loaded_index.d}"
)

print(
    f"Vectors stored   : {loaded_index.ntotal}"
)

print(
    f"Expected vectors : {len(metadata)}"
)

if loaded_index.ntotal != len(metadata):

    raise ValueError(
        "FAISS vector count does not match metadata count."
    )

print()
print("FAISS index validation: PASSED")

print()
print("=" * 60)
print("FAISS INDEX CREATED")
print("=" * 60)

print(
    f"Saved to: {INDEX_FILE}"
)
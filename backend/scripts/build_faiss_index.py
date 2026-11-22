import numpy as np
import faiss
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDINGS_PATH = Path(
    "embeddings/embeddings.npy"
)

INDEX_DIR = Path("index")

INDEX_PATH = INDEX_DIR / "legal_judgments.faiss"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BUILDING FAISS INDEX")
    print("=" * 60)

    # --------------------------------------------------------
    # CREATE INDEX DIRECTORY
    # --------------------------------------------------------

    INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LOAD EMBEDDINGS
    # --------------------------------------------------------

    print()
    print("Loading embeddings...")

    embeddings = np.load(
        EMBEDDINGS_PATH
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    print(
        f"Data type: {embeddings.dtype}"
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D matrix."
        )

    num_vectors = embeddings.shape[0]
    dimensions = embeddings.shape[1]

    print()
    print(f"Number of vectors: {num_vectors}")
    print(f"Dimensions: {dimensions}")

    # --------------------------------------------------------
    # CHECK NORMALIZATION
    # --------------------------------------------------------

    first_norm = np.linalg.norm(
        embeddings[0]
    )

    print(
        f"First vector norm: {first_norm:.6f}"
    )

    # --------------------------------------------------------
    # CREATE FAISS INDEX
    # --------------------------------------------------------

    print()
    print("Creating IndexFlatIP...")

    index = faiss.IndexFlatIP(
        dimensions
    )

    print("Index created.")

    # --------------------------------------------------------
    # ADD EMBEDDINGS
    # --------------------------------------------------------

    print()
    print("Adding embeddings to FAISS...")

    index.add(
        embeddings
    )

    print("Embeddings added.")

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    print()
    print(
        f"FAISS index vectors: {index.ntotal}"
    )

    if index.ntotal != num_vectors:
        raise ValueError(
            "FAISS vector count does not match embeddings."
        )

    # --------------------------------------------------------
    # SAVE INDEX
    # --------------------------------------------------------

    print()
    print(
        f"Saving FAISS index to:\n{INDEX_PATH}"
    )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FAISS INDEX BUILD COMPLETE")
    print("=" * 60)

    print(
        f"Vectors indexed: {index.ntotal}"
    )

    print(
        f"Vector dimensions: {dimensions}"
    )

    print(
        f"Index type: IndexFlatIP"
    )

    print(
        f"Index file: {INDEX_PATH}"
    )


if __name__ == "__main__":
    main()
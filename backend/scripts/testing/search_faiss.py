import sqlite3
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "law-ai/InLegalBERT"

INDEX_PATH = Path(
    "index/legal_judgments.faiss"
)

DATABASE_PATH = Path(
    "embeddings/metadata.db"
)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# MEAN POOLING
# ============================================================

def mean_pooling(last_hidden_state, attention_mask):

    mask = attention_mask.unsqueeze(-1).expand(
        last_hidden_state.size()
    ).float()

    summed = torch.sum(
        last_hidden_state * mask,
        dim=1
    )

    counts = torch.clamp(
        mask.sum(dim=1),
        min=1e-9
    )

    return summed / counts


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 80)
print("FAISS RETRIEVAL DIAGNOSTIC")
print("=" * 80)

print(f"Device: {DEVICE}")
print()

print("Loading InLegalBERT...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModel.from_pretrained(
    MODEL_NAME
)

model.to(DEVICE)
model.eval()

print("Model loaded.")
print()


# ============================================================
# LOAD FAISS
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(
    str(INDEX_PATH)
)

print(
    f"FAISS vectors: {index.ntotal}"
)

print()


# ============================================================
# LOAD DATABASE
# ============================================================

print("Connecting to SQLite database...")

connection = sqlite3.connect(
    DATABASE_PATH
)

cursor = connection.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM chunks"
)

count = cursor.fetchone()[0]

print(
    f"Database records: {count}"
)

print()


# ============================================================
# GET CHUNK
# ============================================================

def get_chunk(connection, vector_id):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            vector_id,
            chunk_id,
            source_file,
            year,
            pages,
            case_title,
            date,
            citation,
            bench,
            petitioner,
            respondent,
            chunk_index,
            word_count,
            text
        FROM chunks
        WHERE vector_id = ?
        """,
        (vector_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "vector_id": row[0],
        "chunk_id": row[1],
        "source_file": row[2],
        "year": row[3],
        "pages": row[4],
        "case_title": row[5],
        "date": row[6],
        "citation": row[7],
        "bench": row[8],
        "petitioner": row[9],
        "respondent": row[10],
        "chunk_index": row[11],
        "word_count": row[12],
        "text": row[13]
    }


# ============================================================
# TEST QUERIES
# ============================================================

queries = [

    "What is the basic structure doctrine of the Constitution?",

    "basic structure doctrine Constitution",

    "constitutional amendment basic structure doctrine Parliament judicial review"

]


# ============================================================
# RUN DIAGNOSTIC
# ============================================================

for query in queries:

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    # --------------------------------------------------------
    # CREATE QUERY EMBEDDING
    # --------------------------------------------------------

    inputs = tokenizer(
        query,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(
            **inputs
        )

    # Mean pooling

    query_embedding = mean_pooling(
        outputs.last_hidden_state,
        inputs["attention_mask"]
    )

    # Normalize

    query_embedding = torch.nn.functional.normalize(
        query_embedding,
        p=2,
        dim=1
    )

    query_embedding_np = (
        query_embedding
        .cpu()
        .numpy()
        .astype("float32")
    )

    # --------------------------------------------------------
    # EMBEDDING DIAGNOSTICS
    # --------------------------------------------------------

    print()

    print(
        "Embedding norm:",
        np.linalg.norm(query_embedding_np)
    )

    print(
        "First 5 values:",
        query_embedding_np[0][:5]
    )

    # --------------------------------------------------------
    # FAISS SEARCH
    # --------------------------------------------------------

    scores, indices = index.search(
        query_embedding_np,
        5
    )

    print()
    print("FAISS RESULTS:")
    print()

    for rank, (score, index_id) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        print(
            f"Rank {rank}: "
            f"FAISS index={index_id}, "
            f"score={score:.4f}"
        )

        row = get_chunk(
            connection,
            int(index_id)
        )

        if row:

            print(
                "Vector ID:",
                row["vector_id"]
            )

            print(
                "Case:",
                row["case_title"]
            )

            print(
                "Chunk:",
                row["chunk_index"]
            )

            print(
                "Words:",
                row["word_count"]
            )

            print(
                "Preview:",
                row["text"][:300]
            )

        else:

            print(
                "NO SQLITE RECORD FOUND"
            )

        print("-" * 60)

# ============================================================
# SELF-RETRIEVAL TEST
# ============================================================

# print()
# print("=" * 80)
# print("SELF-RETRIEVAL TEST")
# print("=" * 80)

# # Pick an existing vector from SQLite
# test_vector_id = 92739

# test_chunk = get_chunk(
#     connection,
#     test_vector_id
# )

# if test_chunk is None:

#     print(
#         "ERROR: Test vector not found in SQLite."
#     )

# else:

#     print(
#         "Testing vector:",
#         test_vector_id
#     )

#     print(
#         "Case:",
#         test_chunk["case_title"]
#     )

#     print(
#         "Chunk:",
#         test_chunk["chunk_index"]
#     )

#     print(
#         "Text preview:",
#         test_chunk["text"][:300]
#     )

#     # --------------------------------------------------------
#     # CREATE EMBEDDING FROM THE ACTUAL CHUNK TEXT
#     # --------------------------------------------------------

#     inputs = tokenizer(
#         test_chunk["text"],
#         return_tensors="pt",
#         truncation=True,
#         max_length=512
#     )

#     inputs = {
#         key: value.to(DEVICE)
#         for key, value in inputs.items()
#     }

#     with torch.no_grad():

#         outputs = model(
#             **inputs
#         )

#     test_embedding = mean_pooling(
#         outputs.last_hidden_state,
#         inputs["attention_mask"]
#     )

#     test_embedding = torch.nn.functional.normalize(
#         test_embedding,
#         p=2,
#         dim=1
#     )

#     test_embedding_np = (
#         test_embedding
#         .cpu()
#         .numpy()
#         .astype("float32")
#     )

#     print()
#     print(
#         "Embedding norm:",
#         np.linalg.norm(test_embedding_np)
#     )

#     # --------------------------------------------------------
#     # SEARCH THE SAME EMBEDDING
#     # --------------------------------------------------------

#     scores, indices = index.search(
#         test_embedding_np,
#         5
#     )

#     print()
#     print("SELF-RETRIEVAL RESULTS:")
#     print()

#     for rank, (score, index_id) in enumerate(
#         zip(scores[0], indices[0]),
#         start=1
#     ):

#         row = get_chunk(
#             connection,
#             int(index_id)
#         )

#         print(
#             f"Rank {rank}: "
#             f"FAISS index={index_id}, "
#             f"score={score:.6f}"
#         )

#         if row:

#             print(
#                 "Vector ID:",
#                 row["vector_id"]
#             )

#             print(
#                 "Case:",
#                 row["case_title"]
#             )

#             print(
#                 "Chunk:",
#                 row["chunk_index"]
#             )

#         print("-" * 60)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
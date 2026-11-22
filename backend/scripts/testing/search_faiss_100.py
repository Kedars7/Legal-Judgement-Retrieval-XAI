import json
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "law-ai/InLegalBERT"

INDEX_FILE = Path(
    "index/baseline_100/legal_judgments.faiss"
)

METADATA_FILE = Path(
    "embeddings/baseline_100/metadata.jsonl"
)

TOP_K = 10

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModel.from_pretrained(
    MODEL_NAME
)

model.to(DEVICE)
model.eval()


# ============================================================
# LOAD FAISS
# ============================================================

index = faiss.read_index(
    str(INDEX_FILE)
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

        if line.strip():
            metadata.append(
                json.loads(line)
            )


# ============================================================
# MEAN POOLING
# ============================================================

def mean_pooling(
    model_output,
    attention_mask
):

    token_embeddings = (
        model_output.last_hidden_state
    )

    input_mask_expanded = (
        attention_mask
        .unsqueeze(-1)
        .expand(token_embeddings.size())
        .float()
    )

    return torch.sum(
        token_embeddings *
        input_mask_expanded,
        dim=1
    ) / torch.clamp(
        input_mask_expanded.sum(dim=1),
        min=1e-9
    )


# ============================================================
# SEARCH
# ============================================================

def search(query):

    encoded = tokenizer(
        [query],
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    encoded = {
        key: value.to(DEVICE)
        for key, value in encoded.items()
    }

    with torch.no_grad():

        output = model(
            **encoded
        )

        embedding = mean_pooling(
            output,
            encoded["attention_mask"]
        )

        embedding = torch.nn.functional.normalize(
            embedding,
            p=2,
            dim=1
        )

    query_vector = (
        embedding
        .cpu()
        .numpy()
        .astype(np.float32)
    )

    scores, ids = index.search(
        query_vector,
        TOP_K
    )

    print()
    print("=" * 80)
    print("QUERY")
    print("=" * 80)

    print(query)

    print()
    print("=" * 80)
    print("TOP RESULTS")
    print("=" * 80)

    for rank, (score, vector_id) in enumerate(
        zip(scores[0], ids[0]),
        start=1
    ):

        if vector_id < 0:
            continue

        item = metadata[vector_id]

        print()
        print(f"Rank       : {rank}")
        print(f"Score      : {score:.4f}")
        print(f"Vector ID  : {vector_id}")
        print(
            f"Case       : "
            f"{item.get('case_title')}"
        )
        print(
            f"Date       : "
            f"{item.get('date')}"
        )
        print(
            f"Chunk ID   : "
            f"{item.get('chunk_id')}"
        )
        print(
            f"Words      : "
            f"{item.get('word_count')}"
        )

        print(
            "Text       : "
            + item.get("text", "")[:500]
            .replace("\n", " ")
        )

        print("-" * 80)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    query = input(
        "\nEnter legal query: "
    ).strip()

    if query:
        search(query)
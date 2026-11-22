import json
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "law-ai/InLegalBERT"

INPUT_FILE = Path(
    "data/processed/chunks/baseline/chunks.jsonl"
)

OUTPUT_DIR = Path(
    "embeddings/baseline_100"
)

EMBEDDINGS_FILE = OUTPUT_DIR / "embeddings.npy"
METADATA_FILE = OUTPUT_DIR / "metadata.jsonl"

BATCH_SIZE = 16
MAX_LENGTH = 512


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("INLEGALBERT EMBEDDING GENERATION")
print("=" * 60)

print(f"Model  : {MODEL_NAME}")
print(f"Device : {DEVICE}")
print()


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Loading model...")

model = AutoModel.from_pretrained(
    MODEL_NAME
)

model.to(DEVICE)
model.eval()

print("Model loaded.")
print()


# ============================================================
# LOAD CHUNKS
# ============================================================

chunks = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if line:
            chunks.append(
                json.loads(line)
            )

print(f"Chunks loaded: {len(chunks)}")
print()


# ============================================================
# MEAN POOLING
# ============================================================

def mean_pooling(
    model_output,
    attention_mask
):
    """
    Mean-pool token embeddings while ignoring padding tokens.
    """

    token_embeddings = model_output.last_hidden_state

    input_mask_expanded = (
        attention_mask
        .unsqueeze(-1)
        .expand(token_embeddings.size())
        .float()
    )

    return torch.sum(
        token_embeddings * input_mask_expanded,
        dim=1
    ) / torch.clamp(
        input_mask_expanded.sum(dim=1),
        min=1e-9
    )


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

all_embeddings = []

for start in tqdm(
    range(
        0,
        len(chunks),
        BATCH_SIZE
    ),
    desc="Embedding chunks"
):

    batch = chunks[
        start:start + BATCH_SIZE
    ]

    texts = [
        item["text"]
        for item in batch
    ]

    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )

    encoded = {
        key: value.to(DEVICE)
        for key, value in encoded.items()
    }

    with torch.no_grad():

        model_output = model(
            **encoded
        )

        embeddings = mean_pooling(
            model_output,
            encoded["attention_mask"]
        )

        # L2 normalization
        embeddings = torch.nn.functional.normalize(
            embeddings,
            p=2,
            dim=1
        )

    all_embeddings.append(
        embeddings.cpu().numpy()
    )


# ============================================================
# COMBINE
# ============================================================

embeddings = np.vstack(
    all_embeddings
).astype(
    np.float32
)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 60)
print("EMBEDDING VALIDATION")
print("=" * 60)

print(
    f"Number of embeddings : {embeddings.shape[0]}"
)

print(
    f"Embedding dimension  : {embeddings.shape[1]}"
)

print(
    f"Data type            : {embeddings.dtype}"
)

# Check for NaN / Inf
print(
    f"Contains NaN         : {np.isnan(embeddings).any()}"
)

print(
    f"Contains Inf         : {np.isinf(embeddings).any()}"
)

# Check norms
norms = np.linalg.norm(
    embeddings,
    axis=1
)

print(
    f"Minimum norm         : {norms.min():.6f}"
)

print(
    f"Maximum norm         : {norms.max():.6f}"
)

print(
    f"Average norm         : {norms.mean():.6f}"
)


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

np.save(
    EMBEDDINGS_FILE,
    embeddings
)


# ============================================================
# SAVE METADATA
# ============================================================

with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as f:

    for chunk in chunks:

        f.write(
            json.dumps(
                chunk,
                ensure_ascii=False
            )
            + "\n"
        )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 60)
print("EMBEDDING GENERATION COMPLETE")
print("=" * 60)

print(
    f"Embeddings saved : {EMBEDDINGS_FILE}"
)

print(
    f"Metadata saved   : {METADATA_FILE}"
)
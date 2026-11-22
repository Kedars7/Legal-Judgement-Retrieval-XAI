import json
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModel


MODEL_NAME = "law-ai/InLegalBERT"

CHUNKS_DIR = Path("data/processed/final_chunks")


def mean_pooling(last_hidden_state, attention_mask):
    """
    Mean pooling over valid tokens only.
    """

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


def main():

    print("=" * 60)
    print("InLegalBERT TEST")
    print("=" * 60)

    # --------------------------------------------------
    # DEVICE
    # --------------------------------------------------

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Device: {device}")

    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU not detected. Using CPU.")

    print()

    # --------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print("Loading model...")

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    model.to(device)
    model.eval()

    print("Model loaded successfully.")
    print()

    # --------------------------------------------------
    # FIND A CHUNK FILE
    # --------------------------------------------------

    files = list(
        CHUNKS_DIR.glob("*.json")
    )

    if not files:
        print("No chunk files found.")
        return

    # Use the first judgment file
    file_path = files[0]

    print(f"Testing file: {file_path.name}")

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    chunks = data.get("chunks", [])

    if len(chunks) < 3:
        print("Not enough chunks in the selected file.")
        return

    texts = [
        chunks[0]["text"],
        chunks[1]["text"],
        chunks[2]["text"]
    ]

    print(f"Testing {len(texts)} chunks.")
    print()

    # --------------------------------------------------
    # TOKENIZATION
    # --------------------------------------------------

    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    encoded = {
        key: value.to(device)
        for key, value in encoded.items()
    }

    print(
        "Tokenized shape:",
        encoded["input_ids"].shape
    )

    # --------------------------------------------------
    # GENERATE EMBEDDINGS
    # --------------------------------------------------

    with torch.no_grad():

        output = model(
            **encoded
        )

        embeddings = mean_pooling(
            output.last_hidden_state,
            encoded["attention_mask"]
        )

    # Normalize embeddings
    embeddings = torch.nn.functional.normalize(
        embeddings,
        p=2,
        dim=1
    )

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    print()
    print("Embedding shape:")
    print(embeddings.shape)

    print()

    print(
        "Expected:",
        f"({len(texts)}, 768)"
    )

    print()

    print("First embedding:")
    print(embeddings[0][:10])

    print()

    print("Embedding norm:")
    print(
        torch.norm(
            embeddings[0]
        ).item()
    )

    print()
    print("=" * 60)
    print("InLegalBERT TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()
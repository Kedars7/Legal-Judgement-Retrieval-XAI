
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CANDIDATES_FILE = (
    ROOT / "eval" / "hybrid_rrf_tuning" / "unjudged_candidates.csv"
)
METADATA_FILE = ROOT / "embeddings" / "baseline_100" / "metadata.jsonl"
OUTPUT_FILE = ROOT / "eval" / "hybrid_rrf_tuning" / "chunks_for_review.txt"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    candidates = read_csv(CANDIDATES_FILE)

    # Load all chunk metadata, including the exact chunk text.
    metadata_by_chunk = {}

    with METADATA_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)
            metadata_by_chunk[str(item["chunk_id"]).strip()] = item

    # Review each unique query/chunk pair only once.
    unique_candidates = {}
    for row in candidates:
        query_id = str(row.get("query_id", "")).strip()
        chunk_id = str(row.get("chunk_id", "")).strip()

        if query_id and chunk_id:
            unique_candidates[(query_id, chunk_id)] = row

    output = []

    for (query_id, chunk_id), row in sorted(
        unique_candidates.items(),
        key=lambda item: (int(item[0][0]), item[0][1]),
    ):
        item = metadata_by_chunk.get(chunk_id)

        output.append("=" * 100)
        output.append(f"Query ID: {query_id}")
        output.append(f"Chunk ID: {chunk_id}")

        # Display any query or annotation context already present.
        for field in ("query", "search_query", "case_title", "relevance",
                      "review_status", "notes"):
            value = row.get(field, "")
            if value:
                output.append(f"{field}: {value}")

        if item is None:
            output.append("ERROR: Chunk ID not found in metadata.")
        else:
            output.append(f"Judgment: {item.get('case_title', '')}")
            output.append(f"Document ID: {item.get('document_id', '')}")
            output.append(f"Date: {item.get('date', '')}")
            output.append(f"Chunk index: {item.get('chunk_index', '')}")
            output.append(f"Word count: {item.get('word_count', '')}")
            output.append("")
            output.append("CHUNK TEXT:")
            output.append(item.get("text", ""))

        output.append("")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(output), encoding="utf-8")

    print(f"Unique query/chunk pairs: {len(unique_candidates)}")
    print(f"Metadata chunks loaded: {len(metadata_by_chunk)}")
    print(f"Review file saved to: {OUTPUT_FILE}")

    missing = [
        chunk_id
        for _, chunk_id in unique_candidates
        if chunk_id not in metadata_by_chunk
    ]

    if missing:
        print(f"WARNING: {len(missing)} candidate pairs have missing chunk IDs.")
        print("Check chunks_for_review.txt for details.")
    else:
        print("All candidate chunk IDs matched successfully.")


if __name__ == "__main__":
    main()

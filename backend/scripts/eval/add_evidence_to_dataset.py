import csv
import json
import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ============================================================
# FILE PATHS
# ============================================================

INPUT_PATH = (
    PROJECT_ROOT
    / "eval"
    / "relevance_dataset.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "eval"
    / "relevance_dataset_with_evidence.csv"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "embeddings"
    / "baseline_100"
    / "metadata.jsonl"
)


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata():

    metadata_by_chunk = {}

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)

            chunk_id = record.get(
                "chunk_id"
            )

            if chunk_id:
                metadata_by_chunk[chunk_id] = record

    return metadata_by_chunk


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("ADDING EVIDENCE TEXT TO RELEVANCE DATASET")
    print("=" * 80)

    print()
    print(f"Input    : {INPUT_PATH}")
    print(f"Metadata : {METADATA_PATH}")
    print(f"Output   : {OUTPUT_PATH}")

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    print()
    print("Loading chunk metadata...")

    metadata = load_metadata()

    print(
        f"Metadata chunks loaded: {len(metadata)}"
    )

    # --------------------------------------------------------
    # Load existing relevance dataset
    # --------------------------------------------------------

    print()
    print("Loading relevance dataset...")

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

        fieldnames = reader.fieldnames

    print(
        f"Dataset rows: {len(rows)}"
    )

    # --------------------------------------------------------
    # Add evidence
    # --------------------------------------------------------

    matched = 0
    missing = 0

    for row in rows:

        chunk_id = row.get(
            "chunk_id",
            ""
        )

        record = metadata.get(
            chunk_id
        )

        if record:

            row["evidence"] = record.get(
                "text",
                ""
            )

            matched += 1

        else:

            row["evidence"] = ""

            missing += 1

    # --------------------------------------------------------
    # Put evidence before relevance
    # --------------------------------------------------------

    new_fieldnames = []

    for field in fieldnames:

        if field == "relevance":

            new_fieldnames.append(
                "evidence"
            )

        new_fieldnames.append(
            field
        )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=new_fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("EVIDENCE DATASET CREATION COMPLETE")
    print("=" * 80)

    print(
        f"Total rows       : {len(rows)}"
    )

    print(
        f"Evidence matched : {matched}"
    )

    print(
        f"Evidence missing : {missing}"
    )

    print(
        f"Output           : {OUTPUT_PATH}"
    )

    if missing == 0:

        print()
        print(
            "SUCCESS: Evidence is available for every candidate."
        )

    else:

        print()
        print(
            "WARNING: Some chunk IDs could not be found."
        )


if __name__ == "__main__":
    main()
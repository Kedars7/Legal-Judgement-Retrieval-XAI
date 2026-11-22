import json
import sqlite3
from pathlib import Path


INPUT_DIR = Path("data/processed/final_chunks")
OUTPUT_DIR = Path("embeddings")

DB_PATH = OUTPUT_DIR / "metadata.db"


def main():

    print("=" * 60)
    print("CREATING METADATA DATABASE")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(
        INPUT_DIR.glob("*.json")
    )

    print(
        f"Judgment files found: {len(files)}"
    )

    # --------------------------------------------------------
    # CREATE DATABASE
    # --------------------------------------------------------

    connection = sqlite3.connect(
        DB_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            vector_id INTEGER PRIMARY KEY,
            chunk_id TEXT,
            source_file TEXT,
            year TEXT,
            pages INTEGER,
            case_title TEXT,
            date TEXT,
            citation TEXT,
            bench TEXT,
            petitioner TEXT,
            respondent TEXT,
            chunk_index INTEGER,
            word_count INTEGER,
            text TEXT
        )
    """)

    connection.commit()

    # --------------------------------------------------------
    # INSERT CHUNKS
    # --------------------------------------------------------

    vector_id = 0

    for i, file_path in enumerate(
        files,
        start=1
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        for chunk in data.get(
            "chunks",
            []
        ):

            cursor.execute("""
                INSERT INTO chunks (
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
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vector_id,
                chunk.get("chunk_id"),
                chunk.get("source_file"),
                chunk.get("year"),
                chunk.get("pages"),
                chunk.get("case_title"),
                chunk.get("date"),
                chunk.get("citation"),
                chunk.get("bench"),
                chunk.get("petitioner"),
                chunk.get("respondent"),
                chunk.get("chunk_index"),
                chunk.get("word_count"),
                chunk.get("text")
            ))

            vector_id += 1

        if i % 500 == 0 or i == len(files):

            connection.commit()

            print(
                f"Processed {i}/{len(files)} | "
                f"Records: {vector_id}"
            )

    connection.commit()

    # --------------------------------------------------------
    # INDEXES
    # --------------------------------------------------------

    print()
    print("Creating database indexes...")

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_case_title
        ON chunks(case_title)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_year
        ON chunks(year)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_citation
        ON chunks(citation)
    """)

    connection.commit()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM chunks"
    )

    total = cursor.fetchone()[0]

    connection.close()

    print()
    print("=" * 60)
    print("DATABASE CREATION COMPLETE")
    print("=" * 60)

    print(
        f"Total records: {total}"
    )

    print(
        f"Database: {DB_PATH}"
    )


if __name__ == "__main__":
    main()
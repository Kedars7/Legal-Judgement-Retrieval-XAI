import json
import re
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path("data/processed/cleaned_100")
OUTPUT_DIR = Path("data/processed/chunks/baseline")

TARGET_MIN_WORDS = 150
TARGET_MAX_WORDS = 300


# ============================================================
# HELPERS
# ============================================================

def count_words(text):
    return len(text.split())


def normalize_text(text):
    """
    Normalize whitespace while preserving paragraph boundaries.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces/tabs inside lines
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_paragraphs(text):
    """
    Split judgment text into paragraphs.

    Blank lines are treated as paragraph boundaries.
    """
    text = normalize_text(text)

    paragraphs = re.split(r"\n\s*\n", text)

    paragraphs = [
        p.strip()
        for p in paragraphs
        if p.strip()
    ]

    return paragraphs


def split_large_paragraph(paragraph, max_words):
    """
    Fallback for paragraphs that are themselves larger
    than the maximum chunk size.

    Split on sentence boundaries where possible.
    """
    words = paragraph.split()

    if len(words) <= max_words:
        return [paragraph]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        paragraph
    )

    pieces = []
    current = []

    for sentence in sentences:

        sentence_words = sentence.split()

        if not sentence_words:
            continue

        # If adding this sentence exceeds max_words,
        # finalize current piece.
        if (
            current
            and len(current) + len(sentence_words) > max_words
        ):
            pieces.append(" ".join(current))
            current = []

        # Extremely long single sentence
        if len(sentence_words) > max_words:

            if current:
                pieces.append(" ".join(current))
                current = []

            for i in range(0, len(sentence_words), max_words):
                pieces.append(
                    " ".join(
                        sentence_words[i:i + max_words]
                    )
                )

        else:
            current.extend(sentence_words)

    if current:
        pieces.append(" ".join(current))

    return pieces


def create_chunks(text):
    """
    Create paragraph-aware baseline chunks.

    Target:
        150–300 words

    Priority:
        paragraph boundaries > exact word count
    """

    paragraphs = split_into_paragraphs(text)

    # First handle extremely large paragraphs.
    processed_paragraphs = []

    for paragraph in paragraphs:

        if count_words(paragraph) > TARGET_MAX_WORDS:
            processed_paragraphs.extend(
                split_large_paragraph(
                    paragraph,
                    TARGET_MAX_WORDS
                )
            )
        else:
            processed_paragraphs.append(paragraph)

    chunks = []

    current_paragraphs = []
    current_words = 0

    for paragraph in processed_paragraphs:

        paragraph_words = count_words(paragraph)

        # Start a new chunk if this paragraph would make
        # the current chunk too large.
        if (
            current_paragraphs
            and current_words + paragraph_words > TARGET_MAX_WORDS
        ):
            chunks.append(
                "\n\n".join(current_paragraphs)
            )

            current_paragraphs = []
            current_words = 0

        current_paragraphs.append(paragraph)
        current_words += paragraph_words

        # Once we have reached the minimum target,
        # close the chunk.
        if current_words >= TARGET_MIN_WORDS:

            chunks.append(
                "\n\n".join(current_paragraphs)
            )

            current_paragraphs = []
            current_words = 0

    # Remaining paragraphs
    if current_paragraphs:
        chunks.append(
            "\n\n".join(current_paragraphs)
        )

    return chunks


# ============================================================
# PROCESS ONE DOCUMENT
# ============================================================

def process_document(json_file):

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:
        document = json.load(f)

    text = document.get("text", "").strip()

    if not text:
        return []

    document_id = Path(
        document["source_file"]
    ).stem

    chunks = create_chunks(text)

    results = []

    search_position = 0

    for index, chunk_text in enumerate(chunks):

        # Character offsets in the cleaned document
        char_start = text.find(
            chunk_text,
            search_position
        )

        if char_start == -1:
            char_start = search_position

        char_end = char_start + len(chunk_text)

        search_position = char_end

        results.append({
            "document_id": document_id,
            "parent_document_id": document_id,

            "chunk_id": f"{document_id}_chunk_{index:04d}",

            "case_title": document.get(
                "case_title"
            ),

            "date": document.get(
                "date"
            ),

            "year": document.get(
                "year"
            ),

            "citation": document.get(
                "citation"
            ),

            "bench": document.get(
                "bench"
            ),

            "petitioner": document.get(
                "petitioner"
            ),

            "respondent": document.get(
                "respondent"
            ),

            "section": "UNKNOWN",

            "chunking_strategy": "baseline",

            "chunk_index": index,

            "text": chunk_text,

            "word_count": count_words(
                chunk_text
            ),

            "char_start": char_start,

            "char_end": char_end
        })

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    json_files = sorted(
        INPUT_DIR.glob("*.json")
    )

    print("=" * 60)
    print("BASELINE LEGAL JUDGMENT CHUNKING")
    print("=" * 60)

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Documents found : {len(json_files)}")
    print()

    all_chunks = []

    documents_processed = 0

    for i, json_file in enumerate(
        json_files,
        start=1
    ):

        chunks = process_document(
            json_file
        )

        all_chunks.extend(chunks)

        documents_processed += 1

        print(
            f"[{i}/{len(json_files)}] "
            f"{json_file.name} "
            f"→ {len(chunks)} chunks"
        )

    # --------------------------------------------------------
    # Save JSONL
    # --------------------------------------------------------

    chunks_file = OUTPUT_DIR / "chunks.jsonl"

    with open(
        chunks_file,
        "w",
        encoding="utf-8"
    ) as f:

        for chunk in all_chunks:

            f.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False
                )
                + "\n"
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    word_counts = [
        chunk["word_count"]
        for chunk in all_chunks
    ]

    if word_counts:

        min_words = min(word_counts)
        max_words = max(word_counts)

        avg_words = (
            sum(word_counts)
            / len(word_counts)
        )

        below_min = sum(
            w < TARGET_MIN_WORDS
            for w in word_counts
        )

        within_target = sum(
            TARGET_MIN_WORDS <= w <= TARGET_MAX_WORDS
            for w in word_counts
        )

        above_max = sum(
            w > TARGET_MAX_WORDS
            for w in word_counts
        )

    else:

        min_words = 0
        max_words = 0
        avg_words = 0
        below_min = 0
        within_target = 0
        above_max = 0

    stats = {
        "chunking_strategy": "baseline",

        "documents_processed": documents_processed,

        "total_chunks": len(all_chunks),

        "target_min_words": TARGET_MIN_WORDS,
        "target_max_words": TARGET_MAX_WORDS,

        "min_words": min_words,
        "average_words": round(
            avg_words,
            2
        ),
        "max_words": max_words,

        "chunks_below_min": below_min,
        "chunks_within_target": within_target,
        "chunks_above_max": above_max
    }

    stats_file = OUTPUT_DIR / "stats.json"

    with open(
        stats_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            stats,
            f,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("CHUNKING COMPLETE")
    print("=" * 60)

    print(
        f"Documents processed : {documents_processed}"
    )

    print(
        f"Total chunks        : {len(all_chunks)}"
    )

    print(
        f"Minimum words       : {min_words}"
    )

    print(
        f"Average words       : {avg_words:.2f}"
    )

    print(
        f"Maximum words       : {max_words}"
    )

    print(
        f"Below 150 words     : {below_min}"
    )

    print(
        f"150–300 words       : {within_target}"
    )

    print(
        f"Above 300 words     : {above_max}"
    )

    print()
    print(f"Chunks saved to     : {chunks_file}")
    print(f"Statistics saved to : {stats_file}")


if __name__ == "__main__":
    main()
import json
import re
from pathlib import Path

INPUT_DIR = Path("data/processed/chunks")
OUTPUT_DIR = Path("data/processed/final_chunks")

MIN_WORDS = 100
TARGET_WORDS = 220
MAX_WORDS = 400


def word_count(text):
    return len(text.split())


def split_sentences(text):
    """
    Split text while trying to preserve sentence boundaries.
    """
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def split_large_chunk(text):
    """
    Split an oversized chunk into approximately TARGET_WORDS
    while preserving sentence boundaries.
    """

    sentences = split_sentences(text)

    result = []
    current = []
    current_words = 0

    for sentence in sentences:

        words = word_count(sentence)

        # If a single sentence itself is > MAX_WORDS,
        # split it by words as a last resort.
        if words > MAX_WORDS:

            if current:
                result.append(" ".join(current))
                current = []
                current_words = 0

            sentence_words = sentence.split()

            for i in range(0, len(sentence_words), TARGET_WORDS):
                part = " ".join(
                    sentence_words[i:i + TARGET_WORDS]
                )

                result.append(part)

            continue

        if current and current_words + words > TARGET_WORDS:
            result.append(" ".join(current))
            current = []
            current_words = 0

        current.append(sentence)
        current_words += words

    if current:
        result.append(" ".join(current))

    return result


def merge_small_chunks(chunks):
    """
    Merge chunks smaller than MIN_WORDS with neighboring chunks.

    We prefer merging a small chunk with the previous chunk.
    If that would become too large, merge it with the next chunk.
    """

    if not chunks:
        return []

    result = []
    i = 0

    while i < len(chunks):

        current = chunks[i]
        current_words = word_count(current)

        # Normal chunk
        if current_words >= MIN_WORDS:
            result.append(current)
            i += 1
            continue

        # Very small first chunk -> merge with next
        if not result:

            if i + 1 < len(chunks):
                merged = current + " " + chunks[i + 1]

                # If merged result is still reasonable
                if word_count(merged) <= MAX_WORDS:
                    result.append(merged)
                    i += 2
                    continue

            result.append(current)
            i += 1
            continue

        # Try merging with previous chunk
        previous = result[-1]
        merged_previous = previous + " " + current

        if word_count(merged_previous) <= MAX_WORDS:
            result[-1] = merged_previous
            i += 1
            continue

        # Otherwise merge with next chunk
        if i + 1 < len(chunks):

            merged_next = current + " " + chunks[i + 1]

            if word_count(merged_next) <= MAX_WORDS:
                result.append(merged_next)
                i += 2
                continue

        # If no safe merge is possible, keep it
        result.append(current)
        i += 1

    return result


def process_judgment(data):

    original_chunks = data.get("chunks", [])

    if not original_chunks:
        return [], 0, 0

    # Extract text only
    texts = [
        chunk.get("text", "").strip()
        for chunk in original_chunks
        if chunk.get("text", "").strip()
    ]

    original_count = len(texts)

    # --------------------------------------------------
    # STEP 1: SPLIT OVERSIZED CHUNKS
    # --------------------------------------------------

    normalized = []

    for text in texts:

        if word_count(text) > MAX_WORDS:
            normalized.extend(
                split_large_chunk(text)
            )
        else:
            normalized.append(text)

    # --------------------------------------------------
    # STEP 2: MERGE SMALL CHUNKS
    # --------------------------------------------------

    cleaned = merge_small_chunks(normalized)

    return cleaned, original_count, len(cleaned)


def build_chunk(chunk_text, metadata, index):

    return {
        "chunk_id": f"{metadata['source_file']}_chunk_{index}",

        "source_file": metadata.get("source_file"),
        "year": metadata.get("year"),
        "pages": metadata.get("pages"),

        "case_title": metadata.get("case_title"),
        "date": metadata.get("date"),
        "citation": metadata.get("citation"),
        "bench": metadata.get("bench"),
        "petitioner": metadata.get("petitioner"),
        "respondent": metadata.get("respondent"),

        "chunk_index": index,
        "word_count": word_count(chunk_text),
        "text": chunk_text
    }


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = list(
        INPUT_DIR.glob("*.json")
    )

    print("=" * 60)
    print("CHUNK QUALITY CLEANUP")
    print("=" * 60)

    print(f"Judgment files found: {len(files)}")
    print(f"Minimum target: {MIN_WORDS} words")
    print(f"Target size: ~{TARGET_WORDS} words")
    print(f"Maximum target: {MAX_WORDS} words")
    print()

    total_original = 0
    total_final = 0
    judgments_changed = 0
    failed = 0

    all_sizes = []

    for i, file_path in enumerate(files, start=1):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            cleaned_texts, original_count, final_count = (
                process_judgment(data)
            )

            total_original += original_count
            total_final += final_count

            if original_count != final_count:
                judgments_changed += 1

            metadata = {
                "source_file": data.get("source_file"),
                "year": data.get("year"),
                "pages": data.get("pages"),
                "case_title": None,
                "date": None,
                "citation": None,
                "bench": None,
                "petitioner": None,
                "respondent": None,
            }

            # Metadata is stored inside the original chunks.
            # Take it from the first chunk.
            if data.get("chunks"):

                first = data["chunks"][0]

                for field in [
                    "case_title",
                    "date",
                    "citation",
                    "bench",
                    "petitioner",
                    "respondent"
                ]:
                    metadata[field] = first.get(field)

            final_chunks = []

            for index, text in enumerate(cleaned_texts):

                chunk = build_chunk(
                    text,
                    metadata,
                    index
                )

                final_chunks.append(chunk)
                all_sizes.append(
                    chunk["word_count"]
                )

            output_data = {
                "source_file": data.get("source_file"),
                "total_chunks": len(final_chunks),
                "chunks": final_chunks
            }

            output_file = OUTPUT_DIR / file_path.name

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    output_data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            if i % 500 == 0 or i == len(files):

                print(
                    f"Processed {i}/{len(files)} | "
                    f"Final chunks: {total_final + final_count}"
                )

        except Exception as e:

            failed += 1

            print()
            print(f"ERROR: {file_path.name}")
            print(e)

    print()
    print("=" * 60)
    print("CHUNK CLEANUP COMPLETE")
    print("=" * 60)

    print(f"Judgments processed: {len(files) - failed}")
    print(f"Failed: {failed}")

    print()
    print(f"Original chunks: {total_original}")
    print(f"Final chunks: {total_final}")
    print(f"Judgments changed: {judgments_changed}")

    if all_sizes:

        print()
        print("FINAL CHUNK STATISTICS")

        print(f"Average words/chunk: "
              f"{sum(all_sizes) / len(all_sizes):.2f}")

        print(f"Minimum words: {min(all_sizes)}")
        print(f"Maximum words: {max(all_sizes)}")

        print(
            f"<100 words: "
            f"{sum(x < 100 for x in all_sizes)}"
        )

        print(
            f"100-400 words: "
            f"{sum(100 <= x <= 400 for x in all_sizes)}"
        )

        print(
            f">400 words: "
            f"{sum(x > 400 for x in all_sizes)}"
        )

    print()
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
import json
import re
from pathlib import Path
from datetime import datetime

INPUT_DIR = Path("data/processed/cleaned")


def extract_date(text, filename):
    """
    Try to extract judgment date from text or filename.
    """

    patterns = [
        r"\bon\s+(\d{1,2}\s+[A-Za-z]+\s*,?\s+\d{4})",
        r"\bdated\s+(\d{1,2}\s+[A-Za-z]+\s*,?\s+\d{4})",
        r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(",", "").strip()

            for fmt in ("%d %B %Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
                except ValueError:
                    pass

    # Try filename
    match = re.search(
        r"_on_(\d{1,2})_([A-Za-z]+)_(\d{4})",
        filename,
        re.IGNORECASE
    )

    if match:
        day, month, year = match.groups()

        try:
            date_obj = datetime.strptime(
                f"{day} {month} {year}",
                "%d %B %Y"
            )
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass

    return None


def extract_citation(text):
    """
    Extract citation from common judgment formats.
    """

    patterns = [
        r"Equivalent citations?\s*:\s*([^\n]+)",
        r"CITATION\s*:\s*([^\n]+)",
        r"Equivalent citations?\s*:\s*([^\r\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            citation = match.group(1).strip()

            if citation:
                return citation

    return None


def extract_case_title(text, filename):
    """
    Extract case title from the beginning of the judgment.
    """

    patterns = [
        r"^(.+?)\s+vs\.?\s+(.+?)(?:\s+on\s+\d{1,2}\s+[A-Za-z]+|\s+Equivalent citations?:)",
        r"^(.+?)\s+v\.?\s+(.+?)(?:\s+on\s+\d{1,2}\s+[A-Za-z]+|\s+Equivalent citations?:)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE
        )

        if match:
            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()

            if petitioner and respondent:
                return f"{petitioner} vs {respondent}"

    # Fallback: derive from filename
    name = Path(filename).stem

    match = re.match(
        r"\d{4}_(.+?)_on_\d{1,2}_[A-Za-z]+_\d{4}",
        name,
        re.IGNORECASE
    )

    if match:
        title = match.group(1)
        title = title.replace("_", " ")
        title = re.sub(r"\s+", " ", title).strip()
        return title

    return None


def extract_parties(case_title):
    """
    Extract petitioner and respondent from case title.
    """

    if not case_title:
        return None, None

    patterns = [
        r"(.+?)\s+vs\.?\s+(.+)",
        r"(.+?)\s+v\.?\s+(.+)",
    ]

    for pattern in patterns:
        match = re.match(pattern, case_title, re.IGNORECASE)

        if match:
            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()

            return petitioner, respondent

    return None, None


def extract_bench(text):
    """
    Extract bench/judge information from common formats.
    """

    patterns = [
        r"JUDGMENT\s*\n\s*([A-Z][^\n]{1,150})",
        r"BENCH\s*:\s*([^\n]+)",
        r"Author/Bench\s*:\s*([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1).strip()

            if value:
                return value

    return None


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_missing = []

    fields = [
        "case_title",
        "date",
        "citation",
        "bench",
        "petitioner",
        "respondent",
    ]

    for field in fields:
        if not data.get(field):
            original_missing.append(field)

    text = data.get("text", "")
    filename = data.get("source_file", file_path.name)

    # --------------------------------------------------
    # CASE TITLE
    # --------------------------------------------------

    if not data.get("case_title"):
        case_title = extract_case_title(text, filename)

        if case_title:
            data["case_title"] = case_title

    # --------------------------------------------------
    # DATE
    # --------------------------------------------------

    if not data.get("date"):
        date = extract_date(text, filename)

        if date:
            data["date"] = date

    # --------------------------------------------------
    # CITATION
    # --------------------------------------------------

    if not data.get("citation"):
        citation = extract_citation(text)

        if citation:
            data["citation"] = citation

    # --------------------------------------------------
    # PETITIONER + RESPONDENT
    # --------------------------------------------------

    if not data.get("petitioner") or not data.get("respondent"):

        petitioner, respondent = extract_parties(
            data.get("case_title")
        )

        if not data.get("petitioner") and petitioner:
            data["petitioner"] = petitioner

        if not data.get("respondent") and respondent:
            data["respondent"] = respondent

    # --------------------------------------------------
    # BENCH
    # --------------------------------------------------

    if not data.get("bench"):
        bench = extract_bench(text)

        if bench:
            data["bench"] = bench

    return data, original_missing


def main():

    files = list(INPUT_DIR.glob("*.json"))

    print("=" * 60)
    print("METADATA VALIDATION AND FIX")
    print("=" * 60)

    print(f"JSON files found: {len(files)}")

    if not files:
        print("No JSON files found.")
        return

    total_fixed = 0
    field_fixed = {
        "case_title": 0,
        "date": 0,
        "citation": 0,
        "bench": 0,
        "petitioner": 0,
        "respondent": 0,
    }

    still_missing = {
        "case_title": 0,
        "date": 0,
        "citation": 0,
        "bench": 0,
        "petitioner": 0,
        "respondent": 0,
    }

    for i, file_path in enumerate(files, start=1):

        try:
            data, original_missing = process_file(file_path)

            # Count fields that were successfully recovered
            for field in original_missing:

                if data.get(field):
                    field_fixed[field] += 1

            # Count fields still missing
            for field in still_missing:

                if not data.get(field):
                    still_missing[field] += 1

            # Save updated JSON
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            if original_missing:
                total_fixed += 1

            if i % 500 == 0 or i == len(files):
                print(f"Processed {i}/{len(files)}")

        except Exception as e:
            print(f"ERROR: {file_path.name}")
            print(e)

    print()
    print("=" * 60)
    print("METADATA FIX COMPLETE")
    print("=" * 60)

    print(f"Files processed: {len(files)}")
    print()

    print("Recovered fields:")
    for field, count in field_fixed.items():
        print(f"  {field}: {count}")

    print()
    print("Still missing:")
    for field, count in still_missing.items():
        print(f"  {field}: {count}")

    print()
    print(f"Files with at least one missing field checked: {total_fixed}")


if __name__ == "__main__":
    main()
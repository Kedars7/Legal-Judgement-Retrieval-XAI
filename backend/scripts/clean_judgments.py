import json
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path("data/processed/extracted_100")
OUTPUT_DIR = Path("data/processed/cleaned_100")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# BASIC CLEANING
# ============================================================

def normalize_unicode(text):
    text = unicodedata.normalize("NFKC", text)

    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

    return text


def normalize_whitespace(text):
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph separation
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ============================================================
# YEAR
# ============================================================

def extract_year(source_file, text):
    # 1. Try filename/path
    match = re.search(r"(19\d{2}|20\d{2})", source_file)

    if match:
        return match.group(1)

    # 2. Try date
    date_match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](19\d{2}|20\d{2})\b",
        text
    )

    if date_match:
        return date_match.group(3)

    return None


# ============================================================
# DATE
# ============================================================

def extract_date(source_file, text):

    # Filename
    match = re.search(
        r"on_(\d{1,2})_(\w+)_(19\d{2}|20\d{2})",
        source_file,
        re.IGNORECASE
    )

    if match:
        day = int(match.group(1))
        month = match.group(2)
        year = match.group(3)

        months = {
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12"
        }

        if month.lower() in months:
            return f"{day:02d}/{months[month.lower()]}/{year}"

    # Text formats
    patterns = [
        r"\b(\d{1,2})[/-](\d{1,2})[/-](19\d{2}|20\d{2})\b",
        r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(19\d{2}|20\d{2})\b"
    ]

    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12"
    }

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            if len(match.groups()) == 3:

                day = int(match.group(1))
                month = match.group(2)
                year = match.group(3)

                if month.isdigit():
                    return f"{day:02d}/{int(month):02d}/{year}"

                month_num = months.get(month.lower())

                if month_num:
                    return f"{day:02d}/{month_num}/{year}"

    return None


# ============================================================
# CASE TITLE
# ============================================================

def extract_case_title(text, source_file=None):
    """
    Extract the case title conservatively.

    Prefer the filename because the dataset filenames contain
    the case title reliably in the current corpus.

    Example:

    1954_E_D_Sassoon_And_Company_Ltd_vs_The_Commissioner_Of_Income_Tax_Bombay_on_14_May_1954_1.PDF

    becomes:

    E D Sassoon And Company Ltd vs The Commissioner Of Income Tax Bombay
    """

    # --------------------------------------------------------
    # 1. Prefer source filename
    # --------------------------------------------------------

    if source_file:

        filename = Path(source_file).stem

        # Remove trailing "_1", "_2", etc.
        filename = re.sub(
            r"_\d+$",
            "",
            filename
        )

        # Remove date portion:
        # _on_14_May_1954
        filename = re.sub(
            r"_on_\d{1,2}_[A-Za-z]+_\d{4}$",
            "",
            filename,
            flags=re.IGNORECASE
        )

        filename = re.sub(
            r"^\d{4}_",
            "",
            filename
        )

        # Convert underscores to spaces
        title = filename.replace(
            "_",
            " "
        )

        # Normalize whitespace
        title = re.sub(
            r"\s+",
            " ",
            title
        ).strip()

        if title:
            return title

    # --------------------------------------------------------
    # 2. Fallback: extract from text
    # --------------------------------------------------------

    patterns = [
        r"^\s*(.+?)\s+on\s+\d{1,2}\s+[A-Za-z]+,?\s+\d{4}\s*$",
        r"^\s*(.+?)\s+on\s+\d{1,2}\s+[A-Za-z]+\s*,?\s*\d{4}\s*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE |
            re.MULTILINE
        )

        if match:

            title = match.group(1).strip()

            title = re.sub(
                r"\s+",
                " ",
                title
            )

            return title.strip(
                " ,:-"
            )

    return None

    name = Path(source_file).stem

    # Remove numeric year prefix
    name = re.sub(r"^\d{4}_", "", name)

    # Remove trailing PDF numbering
    name = re.sub(r"_\d+$", "", name)

    # Replace underscores
    name = name.replace("_", " ")

    # Remove "on DATE" part
    name = re.sub(
        r"\s+on\s+\d{1,2}\s+\w+\s+\d{4}.*$",
        "",
        name,
        flags=re.IGNORECASE
    )

    return name.strip()


# ============================================================
# CITATION
# ============================================================
def clean_case_title(title):
    """
    Remove date/page-header pollution from case title.
    """

    if not title:
        return None

    title = title.strip()

    # Remove common trailing date/header fragments
    title = re.sub(
        r"\s+on\s+\d{1,2}\s+\w+\s*,?\s*$",
        "",
        title,
        flags=re.IGNORECASE
    )

    # Remove excessive whitespace
    title = re.sub(r"\s+", " ", title)

    return title.strip(" ,:-")

def extract_citation(text):

    # --------------------------------------------------------
    # Equivalent citations
    # --------------------------------------------------------

    match = re.search(
        r"Equivalent citations?\s*:\s*(.*?)(?=\n|Author\s*:|Bench\s*:|JUDGMENT)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        citation = match.group(1).strip()

        citation = re.sub(
            r"\s+",
            " ",
            citation
        )

        # Remove incomplete trailing fragments such as:
        # "AIR 1951 SUPREME"
        citation = re.sub(
            r",?\s*AIR\s+\d{4}\s+SUPREME.*$",
            "",
            citation,
            flags=re.IGNORECASE
        )

        return citation.strip(" ,;:")

    # --------------------------------------------------------
    # CITATION field
    # --------------------------------------------------------

    match = re.search(
        r"\bCITATION\s*:\s*(.*?)(?=\bCITATOR INFO\b|\bACT\s*:|\bHEADNOTE\s*:|\bJUDGMENT\s*:|\n)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        citation = match.group(1).strip()

        citation = re.sub(
            r"\s+",
            " ",
            citation
        )

        citation = re.sub(
            r",?\s*AIR\s+\d{4}\s+SUPREME.*$",
            "",
            citation,
            flags=re.IGNORECASE
        )

        return citation.strip(" ,;:")

    return None

    # --------------------------------------------------------
    # Equivalent citations
    # --------------------------------------------------------

    match = re.search(
        r"Equivalent citations?\s*:\s*(.*?)(?=\n|Author\s*:|Bench\s*:|JUDGMENT)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        citation = match.group(1).strip()

        citation = re.sub(
            r"\s+",
            " ",
            citation
        )

        return citation.strip(" ,;:")

    # --------------------------------------------------------
    # Standard CITATION field
    # --------------------------------------------------------

    match = re.search(
        r"\bCITATION\s*:\s*(.*?)(?=\bCITATOR INFO\b|\bACT\s*:|\bHEADNOTE\s*:|\bJUDGMENT\s*:|\n)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        citation = match.group(1).strip()

        citation = re.sub(
            r"\s+",
            " ",
            citation
        )

        return citation.strip(" ,;:")

    return None

    # First try "Equivalent citations"
    match = re.search(
        r"Equivalent citations?\s*:\s*(.*?)(?:\n|Author\s*:|Bench\s*:|JUDGMENT)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        citation = match.group(1).strip()

        # Keep only first line
        citation = citation.split("\n")[0]

        return citation.strip(" ,;")

    # Try normal citation line
    match = re.search(
        r"CITATION\s*:\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if match:
        citation = match.group(1).strip()

        # Remove trailing unrelated metadata
        citation = re.split(
            r"\b(?:CITATOR INFO|ACT|HEADNOTE|JUDGMENT)\b",
            citation,
            flags=re.IGNORECASE
        )[0]

        return citation.strip(" ,;")

    return None


# ============================================================
# BENCH
# ============================================================

def extract_bench(text):
    """
    Extract bench information conservatively.

    Prefer an explicit Bench: field.
    Otherwise use the metadata/header area when possible.
    """

    # --------------------------------------------------------
    # Explicit Bench field
    # --------------------------------------------------------

    match = re.search(
        r"\bBench\s*:\s*(.*?)(?=\n|Author\s*:|JUDGMENT|$)",
        text,
        re.IGNORECASE
    )

    if match:
        bench = match.group(1).strip()
        bench = re.sub(r"\s+", " ", bench)

        return bench.strip(" ,;:")

    return None

    # Look for explicit Bench field
    match = re.search(
        r"\bBench\s*:\s*(.*?)(?=\s+(?:PETITIONER|RESPONDENT|DATE|CITATION|JUDGMENT|Author)\s*:|\n\s*(?:PETITIONER|RESPONDENT|DATE|CITATION|JUDGMENT)\b)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        bench = match.group(1).strip()

        bench = re.sub(r"\s+", " ", bench)

        return bench.strip(" ,;:")

    # Try repeated BENCH lines
    matches = re.findall(
        r"\bBENCH\s*:\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if matches:

        names = []

        for item in matches:
            item = re.sub(
                r"\b(?:PETITIONER|RESPONDENT|DATE|CITATION)\s*:.*$",
                "",
                item,
                flags=re.IGNORECASE
            )

            item = item.strip(" ,;:")

            if item and item not in names:
                names.append(item)

        if names:
            return "; ".join(names)

    return None


# ============================================================
# PETITIONER / RESPONDENT
# ============================================================

def extract_parties(text):

    petitioner = None
    respondent = None

    # Format:
    # PETITIONER: X Vs. RESPONDENT: Y
    match = re.search(
        r"PETITIONER\s*:\s*(.*?)\s+(?:Vs\.?|V\.?)\s+RESPONDENT\s*:\s*(.*?)(?=\s+(?:DATE|BENCH|CITATION|JUDGMENT)\s*:|\n)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        petitioner = match.group(1).strip()
        respondent = match.group(2).strip()

    # Alternative:
    # X Vs. Y
    if not petitioner:

        match = re.search(
            r"(?:PETITIONER\s*:\s*)?(.{2,150}?)\s+(?:Vs\.?|V\.?)\s+(?:RESPONDENT\s*:\s*)?(.{2,150}?)(?=\s+(?:DATE|BENCH|CITATION|JUDGMENT)\s*:|\n)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()

    return petitioner, respondent


# ============================================================
# REMOVE FRONT MATTER
# ============================================================

def remove_front_matter(text):

    # --------------------------------------------------------
    # Case 1:
    # Explicit JUDGMENT followed by actual judgment
    # --------------------------------------------------------

    judgment_matches = list(
        re.finditer(
            r"\bJUDGMENT\s*:",
            text,
            re.IGNORECASE
        )
    )

    if judgment_matches:

        # Start after the LAST JUDGMENT marker.
        # This avoids stopping at metadata references.
        start = judgment_matches[-1].end()

        candidate = text[start:]

        # Remove leading date/header material
        candidate = re.sub(
            r"^\s*(?:\d{4}\.\s*)?(?:\w+\s+\d{1,2}\.?\s+\d{4}\.?\s*)?",
            "",
            candidate,
            flags=re.IGNORECASE
        )

        # Prefer first numbered paragraph
        numbered = re.search(
            r"\n\s*1\.\s+",
            candidate
        )

        if numbered:
            return candidate[numbered.start():].strip()

        # If no numbered paragraph, keep candidate
        return candidate.strip()

    # --------------------------------------------------------
    # Case 2:
    # Find first numbered paragraph
    # --------------------------------------------------------

    match = re.search(
        r"(?:^|\n)\s*1\.\s+",
        text
    )

    if match:
        return text[match.start():].strip()

    # --------------------------------------------------------
    # Case 3:
    # Some judgments begin directly with date + judgment
    # --------------------------------------------------------

    return text.strip()


def remove_embedded_case_headers(text, case_title, date):
    """
    Remove repeated case-title/date headers embedded inside
    paragraph text.

    Handles OCR/PDF variations such as:
        E D Sassoon
        E. D. Sassoon
        Income Tax
        Income-Tax
        extra punctuation
        whitespace differences
        "... on 14 May, 1954"
    """

    if not case_title or not date:
        return text

    try:
        day, month, year = date.split("/")
    except ValueError:
        return text

    month_names = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    month_name = month_names.get(month)

    if not month_name:
        return text

    # --------------------------------------------------------
    # Build a flexible version of the case title.
    #
    # Example:
    # "E D Sassoon And Company Ltd"
    #
    # can match:
    # "E. D. Sassoon And Company Ltd"
    # --------------------------------------------------------

    title_words = re.findall(
        r"[A-Za-z]+",
        case_title
    )

    if len(title_words) < 3:
        return text

    title_pattern = r"[\s\W_]*".join(
        re.escape(word)
        for word in title_words
    )

    # --------------------------------------------------------
    # Match:
    #
    # <case title> ... on 14 May, 1954
    #
    # The .*? allows punctuation / "..." / OCR artifacts
    # between the title and date.
    # --------------------------------------------------------

    pattern = re.compile(
        rf"\s+{title_pattern}"
        rf".*?"
        rf"\bon\s+"
        rf"{int(day)}\s+{month_name}\s*,?\s*{year}",
        re.IGNORECASE
    )

    text = pattern.sub("", text)

    return text

# ============================================================
# REMOVE NOISE FROM JUDGMENT BODY
# ============================================================

def remove_noise_lines(text, case_title=None, date=None):

    lines = text.splitlines()

    cleaned = []

    # --------------------------------------------------------
    # Build possible repeated title patterns
    # --------------------------------------------------------

    title_pattern = None

    if case_title:

        escaped_title = re.escape(case_title)

        # Example:
        # Arjuna Lal Misra vs The State on 30 November, 1950
        title_pattern = re.compile(
            rf"^\s*{escaped_title}\s+on\s+.*$",
            re.IGNORECASE
        )

    for line in lines:

        stripped = line.strip()

        # Preserve paragraph separation
        if not stripped:
            cleaned.append("")
            continue

        # ----------------------------------------------------
        # Remove repeated case title page headers
        # ----------------------------------------------------

        if title_pattern and title_pattern.match(stripped):
            continue

        # ----------------------------------------------------
        # Remove Indian Kanoon URLs
        # ----------------------------------------------------

        if "indiankanoon.org" in stripped.lower():
            continue

        # ----------------------------------------------------
        # Remove digital signature lines
        # ----------------------------------------------------

        if re.search(
            r"digital\s+signature|signed\s+by",
            stripped,
            re.IGNORECASE
        ):
            continue

        # ----------------------------------------------------
        # Remove standalone page numbers
        # ----------------------------------------------------

        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        cleaned.append(stripped)

    return "\n".join(cleaned)

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            cleaned.append("")
            continue

        # URLs
        if "indiankanoon.org" in stripped.lower():
            continue

        # Digital signatures
        if re.search(
            r"digital\s+signature|signed\s+by",
            stripped,
            re.IGNORECASE
        ):
            continue

        # Page numbers
        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        cleaned.append(stripped)

    return "\n".join(cleaned)


# ============================================================
# NORMALIZE PARAGRAPHS
# ============================================================

def normalize_paragraphs(text):

    text = re.sub(r"[ \t]+", " ", text)

    # Preserve paragraph breaks
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ============================================================
# PROCESS ONE FILE
# ============================================================

def process_file(input_path, output_path):

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_text = data.get("text", "")

    source_file = data.get(
        "source_file",
        input_path.name
    )

    # --------------------------------------------------------
    # Basic normalization
    # --------------------------------------------------------

    text = normalize_unicode(raw_text)

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    year = extract_year(source_file, text)

    date = extract_date(
        source_file,
        text
    )

    case_title = clean_case_title(
    extract_case_title(
        text,
        source_file=source_file
    )
)

    citation = extract_citation(text)

    bench = extract_bench(text)

    petitioner, respondent = extract_parties(text)

    # --------------------------------------------------------
    # Clean judgment body
    # --------------------------------------------------------

    text = remove_front_matter(text)

    text = remove_noise_lines(
    text,
    case_title=case_title,
    date=date
)

    text = remove_embedded_case_headers(
    text,
    case_title=case_title,
    date=date
)

    text = normalize_paragraphs(text)

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    cleaned = {
        "source_file": source_file,
        "year": year,
        "pages": data.get("pages"),
        "case_title": case_title,
        "date": date,
        "citation": citation,
        "bench": bench,
        "petitioner": petitioner,
        "respondent": respondent,
        "text": text
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cleaned,
            f,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# MAIN
# ============================================================

def main():

    files = list(INPUT_DIR.glob("*.json"))

    print(f"Found {len(files)} extracted files.")

    success = 0
    failed = 0

    for input_path in files:

        output_path = OUTPUT_DIR / input_path.name

        try:

            process_file(
                input_path,
                output_path
            )

            success += 1

        except Exception as e:

            failed += 1

            print(
                f"[ERROR] {input_path.name}: {e}"
            )

    print()
    print("========================================")
    print("CLEANING COMPLETE")
    print("========================================")
    print(f"Success : {success}")
    print(f"Failed  : {failed}")
    print(f"Output  : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
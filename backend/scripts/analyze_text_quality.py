from pathlib import Path
import fitz
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supreme_court_judgments"
)


SAMPLE_YEARS = [
    "1950",
    "1960",
    "1970",
    "1980",
    "1990",
    "2000",
    "2010",
    "2020",
    "2025"
]


def get_first_pdf(year):
    year_path = DATASET_PATH / year

    pdfs = sorted(year_path.glob("*.pdf"))

    if not pdfs:
        return None

    return pdfs[0]


def extract_text(pdf_path):

    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def analyze_text(text):

    characters = len(text)

    words = text.split()

    word_count = len(words)

    if word_count > 0:
        avg_word_length = (
            sum(len(word) for word in words)
            / word_count
        )
    else:
        avg_word_length = 0

    # Count spaces
    spaces = text.count(" ")

    # Detect patterns such as:
    # "M u t h a m m a l"
    spaced_char_pattern = re.findall(
        r"\b(?:[A-Za-z]\s+){3,}[A-Za-z]\b",
        text
    )

    # Important legal metadata
    metadata_patterns = {
        "DATE OF JUDGMENT": "DATE OF JUDGMENT",
        "BENCH": "BENCH",
        "CITATION": "CITATION",
        "PETITIONER": "PETITIONER",
        "RESPONDENT": "RESPONDENT",
        "JUDGMENT": "JUDGMENT",
    }

    metadata_found = {}

    for name, pattern in metadata_patterns.items():
        metadata_found[name] = pattern.lower() in text.lower()

    return {
        "characters": characters,
        "words": word_count,
        "avg_word_length": avg_word_length,
        "spaces": spaces,
        "suspicious_spaced_sequences": len(
            spaced_char_pattern
        ),
        "metadata": metadata_found,
    }


print("=" * 70)
print("LEGAL JUDGMENT TEXT QUALITY ANALYSIS")
print("=" * 70)


for year in SAMPLE_YEARS:

    pdf_path = get_first_pdf(year)

    print("\n" + "-" * 70)
    print(f"YEAR: {year}")

    if pdf_path is None:
        print("❌ No PDF found")
        continue

    print(f"File: {pdf_path.name}")

    text = extract_text(pdf_path)

    analysis = analyze_text(text)

    print(f"Characters: {analysis['characters']}")
    print(f"Words: {analysis['words']}")
    print(
        f"Average word length: "
        f"{analysis['avg_word_length']:.2f}"
    )

    print(
        "Suspicious spaced sequences: "
        f"{analysis['suspicious_spaced_sequences']}"
    )

    print("\nMetadata detected:")

    for field, found in analysis["metadata"].items():

        status = "YES" if found else "NO"

        print(f"  {field}: {status}")


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
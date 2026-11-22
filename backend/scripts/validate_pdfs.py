from pathlib import Path
import fitz  # PyMuPDF


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supreme_court_judgments"
)

# Years we want to sample
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


# ============================================================
# FIND A SAMPLE PDF
# ============================================================

def find_sample_pdf(year):
    year_path = DATASET_PATH / year

    if not year_path.exists():
        return None

    pdf_files = sorted(year_path.glob("*.pdf"))

    if not pdf_files:
        return None

    # Select the first PDF for consistency
    return pdf_files[0]


# ============================================================
# VALIDATE PDF
# ============================================================

def validate_pdf(pdf_path):

    result = {
        "file": pdf_path.name,
        "pages": 0,
        "characters": 0,
        "status": "FAILED",
        "sample_text": ""
    }

    try:

        # Open PDF
        document = fitz.open(pdf_path)

        result["pages"] = len(document)

        extracted_text = ""

        # Extract text from every page
        for page in document:
            extracted_text += page.get_text()

        result["characters"] = len(extracted_text)

        # Take first 500 characters for inspection
        result["sample_text"] = (
            extracted_text[:500]
            .replace("\n", " ")
            .strip()
        )

        if result["characters"] > 0:
            result["status"] = "SUCCESS"

        document.close()

    except Exception as e:

        result["status"] = f"ERROR: {e}"

    return result


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("LEGAL JUDGMENT PDF VALIDATION")
print("=" * 70)

print(f"\nDataset:")
print(DATASET_PATH)

print("\n" + "-" * 70)

successful = 0
failed = 0

for year in SAMPLE_YEARS:

    pdf_path = find_sample_pdf(year)

    print(f"\nYEAR: {year}")

    if pdf_path is None:
        print("❌ No PDF found")
        failed += 1
        continue

    result = validate_pdf(pdf_path)

    print(f"File       : {result['file']}")
    print(f"Pages      : {result['pages']}")
    print(f"Characters : {result['characters']}")
    print(f"Status     : {result['status']}")

    if result["sample_text"]:
        print(f"Text sample: {result['sample_text']}")

    if result["status"] == "SUCCESS":
        successful += 1
    else:
        failed += 1


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(f"Samples tested : {len(SAMPLE_YEARS)}")
print(f"Successful     : {successful}")
print(f"Failed         : {failed}")

print("=" * 70)
from pathlib import Path
import csv
import fitz
from datetime import datetime


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

REPORTS_PATH = PROJECT_ROOT / "reports"

REPORTS_PATH.mkdir(exist_ok=True)

OUTPUT_FILE = REPORTS_PATH / "full_corpus_scan.csv"


# ============================================================
# SETTINGS
# ============================================================

# Documents with fewer characters than this will be flagged.
MIN_CHARACTERS = 1000


# ============================================================
# FIND ALL PDFs
# ============================================================

pdf_files = sorted(
    DATASET_PATH.rglob("*.pdf")
)

total_files = len(pdf_files)


print("=" * 70)
print("FULL LEGAL CORPUS QUALITY SCAN")
print("=" * 70)

print(f"\nDataset:")
print(DATASET_PATH)

print(f"\nPDF files found: {total_files}")

print(f"\nScan started at:")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("\n" + "-" * 70)


# ============================================================
# CSV SETUP
# ============================================================

fieldnames = [
    "year",
    "filename",
    "pages",
    "characters",
    "words",
    "status",
    "error"
]


csv_file = open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
)

writer = csv.DictWriter(
    csv_file,
    fieldnames=fieldnames
)

writer.writeheader()


# ============================================================
# STATISTICS
# ============================================================

successful = 0
failed = 0
low_text = 0

total_pages = 0
total_characters = 0
total_words = 0


# ============================================================
# PROCESS PDFs
# ============================================================

for index, pdf_path in enumerate(pdf_files, start=1):

    # --------------------------------------------------------
    # Determine year
    # --------------------------------------------------------

    year = pdf_path.parent.name

    pages = 0
    characters = 0
    words = 0
    status = "SUCCESS"
    error_message = ""


    try:

        # ----------------------------------------------------
        # Open PDF
        # ----------------------------------------------------

        document = fitz.open(pdf_path)

        pages = len(document)

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text()

        document.close()


        # ----------------------------------------------------
        # Calculate statistics
        # ----------------------------------------------------

        characters = len(extracted_text)

        words = len(extracted_text.split())


        # ----------------------------------------------------
        # Check for suspiciously low text
        # ----------------------------------------------------

        if characters < MIN_CHARACTERS:

            status = "LOW_TEXT"

            low_text += 1

        else:

            successful += 1


    except Exception as e:

        status = "FAILED"

        error_message = str(e)

        failed += 1


    # --------------------------------------------------------
    # Update totals
    # --------------------------------------------------------

    total_pages += pages
    total_characters += characters
    total_words += words


    # --------------------------------------------------------
    # Write result
    # --------------------------------------------------------

    writer.writerow({
        "year": year,
        "filename": pdf_path.name,
        "pages": pages,
        "characters": characters,
        "words": words,
        "status": status,
        "error": error_message
    })


    # --------------------------------------------------------
    # Progress display
    # --------------------------------------------------------

    if index % 100 == 0 or index == total_files:

        percentage = (
            index / total_files
        ) * 100

        print(
            f"Progress: {index}/{total_files} "
            f"({percentage:.2f}%) | "
            f"Success: {successful} | "
            f"Low text: {low_text} | "
            f"Failed: {failed}"
        )


# ============================================================
# CLOSE CSV
# ============================================================

csv_file.close()


# ============================================================
# FINAL STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("FULL CORPUS SCAN COMPLETE")
print("=" * 70)

print(f"\nTotal PDFs      : {total_files}")
print(f"Successful      : {successful}")
print(f"Low text        : {low_text}")
print(f"Failed          : {failed}")

print(f"\nTotal pages     : {total_pages:,}")
print(f"Total characters: {total_characters:,}")
print(f"Total words     : {total_words:,}")

if total_files > 0:

    print(
        f"\nAverage pages/document: "
        f"{total_pages / total_files:.2f}"
    )

    print(
        f"Average characters/document: "
        f"{total_characters / total_files:.2f}"
    )

    print(
        f"Average words/document: "
        f"{total_words / total_files:.2f}"
    )

print("\nReport saved to:")

print(OUTPUT_FILE)

print("\n" + "=" * 70)
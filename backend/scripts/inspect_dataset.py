from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

# Project root = one level above the scripts folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supreme_court_judgments"
)


# ============================================================
# CHECK DATASET PATH
# ============================================================

if not DATASET_PATH.exists():
    print("❌ Dataset folder not found!")
    print(f"Expected location: {DATASET_PATH}")
    exit()


print("=" * 60)
print("LEGAL JUDGMENT DATASET INSPECTION")
print("=" * 60)

print(f"\nDataset path:")
print(DATASET_PATH)


# ============================================================
# FIND YEAR FOLDERS
# ============================================================

year_folders = sorted(
    [
        folder
        for folder in DATASET_PATH.iterdir()
        if folder.is_dir() and folder.name.isdigit()
    ],
    key=lambda x: int(x.name)
)


print("\n" + "-" * 60)
print("YEAR INFORMATION")
print("-" * 60)

print(f"Number of year folders: {len(year_folders)}")

if year_folders:
    print(f"First year: {year_folders[0].name}")
    print(f"Last year:  {year_folders[-1].name}")


# ============================================================
# COUNT PDF FILES
# ============================================================

year_counts = Counter()

total_pdfs = 0
total_non_pdfs = 0
empty_pdfs = 0

for year_folder in year_folders:

    pdf_files = list(year_folder.rglob("*.pdf"))

    year_counts[year_folder.name] = len(pdf_files)

    total_pdfs += len(pdf_files)

    # Check for empty PDFs
    for pdf in pdf_files:
        if pdf.stat().st_size == 0:
            empty_pdfs += 1


# ============================================================
# COUNT NON-PDF FILES
# ============================================================

all_files = [
    file
    for file in DATASET_PATH.rglob("*")
    if file.is_file()
]

total_non_pdfs = sum(
    1 for file in all_files
    if file.suffix.lower() != ".pdf"
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "-" * 60)
print("DATASET STATISTICS")
print("-" * 60)

print(f"Total PDF files : {total_pdfs}")
print(f"Non-PDF files   : {total_non_pdfs}")
print(f"Empty PDFs      : {empty_pdfs}")


# ============================================================
# JUDGMENTS PER YEAR
# ============================================================

print("\n" + "-" * 60)
print("JUDGMENTS PER YEAR")
print("-" * 60)

for year, count in year_counts.items():
    print(f"{year}: {count}")


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)
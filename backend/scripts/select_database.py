from pathlib import Path
import shutil
import random

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "supreme_court_judgments"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "judgments"

TARGET_COUNT = 5000
SEED = 42

random.seed(SEED)

# Get PDFs year-wise
year_files = {}

for year_folder in sorted(RAW_PATH.iterdir()):
    if not year_folder.is_dir():
        continue

    pdfs = list(year_folder.glob("*.pdf"))

    if pdfs:
        year_files[year_folder.name] = pdfs

total_available = sum(len(files) for files in year_files.values())

print(f"Total available PDFs: {total_available}")
print(f"Target PDFs: {TARGET_COUNT}")

# Initial proportional allocation
selected = []

for year, files in year_files.items():
    proportion = len(files) / total_available
    count = round(proportion * TARGET_COUNT)

    count = min(count, len(files))

    chosen = random.sample(files, count)
    selected.extend(chosen)

# Adjust if rounding caused count != TARGET_COUNT
if len(selected) < TARGET_COUNT:
    remaining = [
        pdf
        for files in year_files.values()
        for pdf in files
        if pdf not in selected
    ]

    extra = random.sample(remaining, TARGET_COUNT - len(selected))
    selected.extend(extra)

elif len(selected) > TARGET_COUNT:
    selected = random.sample(selected, TARGET_COUNT)

# Copy files
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

for index, pdf in enumerate(selected, start=1):

    year = pdf.parent.name

    output_name = f"{year}_{pdf.name}"
    destination = PROCESSED_PATH / output_name

    shutil.copy2(pdf, destination)

    if index % 500 == 0 or index == len(selected):
        print(f"Copied {index}/{TARGET_COUNT}")

print("\nSelection complete.")
print(f"Selected: {len(selected)} PDFs")
print(f"Output: {PROCESSED_PATH}")
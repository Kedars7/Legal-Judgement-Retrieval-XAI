from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "supreme_court_judgments"
)

print("Non-PDF files:")
print("-" * 60)

count = 0

for file in DATASET_PATH.rglob("*"):
    if file.is_file() and file.suffix.lower() != ".pdf":
        print(f"Name : {file.name}")
        print(f"Path : {file}")
        print(f"Type : {file.suffix or '[no extension]'}")
        print()

        count += 1

print("-" * 60)
print(f"Total non-PDF files: {count}")
import shutil
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path("data/processed/judgments")

OUTPUT_DIR = Path("data/processed/judgments_100")

TARGET_COUNT = 100


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SELECTING 100 MOST RECENT JUDGMENTS")
    print("=" * 70)

    if not INPUT_DIR.exists():
        print(f"ERROR: Input directory does not exist:")
        print(INPUT_DIR.resolve())
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Find all PDFs
    # --------------------------------------------------------

    pdf_files = list(
        INPUT_DIR.rglob("*.pdf")
    )

    print(f"Available PDFs: {len(pdf_files)}")

    if len(pdf_files) < TARGET_COUNT:
        print(
            f"ERROR: Only {len(pdf_files)} PDFs available."
        )
        return

    # --------------------------------------------------------
    # Extract year from path
    #
    # Expected structure:
    #
    # judgments/
    # ├── 1950/
    # ├── 1951/
    # ...
    # └── 2025/
    # --------------------------------------------------------

    def get_year(path):

        for part in path.parts:

            if part.isdigit():

                year = int(part)

                if 1950 <= year <= 2025:
                    return year

        return 0

    # --------------------------------------------------------
    # Sort:
    #
    # 1. Newest year first
    # 2. Filename alphabetically
    #
    # This makes selection deterministic.
    # --------------------------------------------------------

    pdf_files.sort(
        key=lambda p: (
            -get_year(p),
            p.name.lower()
        )
    )

    # --------------------------------------------------------
    # Select first 100
    # --------------------------------------------------------

    selected = pdf_files[:TARGET_COUNT]

    # --------------------------------------------------------
    # Copy files
    # --------------------------------------------------------

    year_counter = Counter()

    for index, source_path in enumerate(
        selected,
        start=1
    ):

        year = get_year(source_path)

        year_counter[year] += 1

        # Keep the year folder structure.
        destination_dir = (
            OUTPUT_DIR / str(year)
        )

        destination_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        destination_path = (
            destination_dir /
            source_path.name
        )

        shutil.copy2(
            source_path,
            destination_path
        )

        print(
            f"[{index:03d}/100] "
            f"{year} - "
            f"{source_path.name}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SELECTION COMPLETE")
    print("=" * 70)

    print(
        f"Selected: {len(selected)} PDFs"
    )

    print(
        f"Output: {OUTPUT_DIR.resolve()}"
    )

    print()
    print("Cases by year:")

    for year in sorted(
        year_counter.keys(),
        reverse=True
    ):

        print(
            f"  {year}: "
            f"{year_counter[year]}"
        )


if __name__ == "__main__":
    main()
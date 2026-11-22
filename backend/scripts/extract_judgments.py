import json
import fitz
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path(
    "data/processed/judgments_100"
)

OUTPUT_DIR = Path(
    "data/processed/extracted_100"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# EXTRACT TEXT FROM ONE PDF
# ============================================================

def extract_pdf(pdf_path):

    document = fitz.open(pdf_path)

    page_texts = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        text = page.get_text("text")

        if text:
            text = text.strip()

        page_texts.append(text)

    document.close()

    # Keep page boundaries.
    #
    # This is important because later we want to detect
    # repeated headers and footers appearing on many pages.
    full_text = "\n\n".join(
        page_texts
    )

    return (
        full_text,
        len(page_texts)
    )


# ============================================================
# PROCESS ALL PDFs
# ============================================================

def main():

    print("=" * 70)
    print("JUDGMENT TEXT EXTRACTION - 100 CASE VERSION")
    print("=" * 70)

    if not INPUT_DIR.exists():

        print(
            f"ERROR: Input directory does not exist:\n"
            f"{INPUT_DIR.resolve()}"
        )

        return

    pdf_files = sorted(
        INPUT_DIR.rglob("*.pdf")
    )

    print(
        f"PDFs found: {len(pdf_files)}"
    )

    if not pdf_files:

        print(
            "ERROR: No PDF files found."
        )

        return

    successful = 0
    failed = 0

    # --------------------------------------------------------
    # Process PDFs
    # --------------------------------------------------------

    for index, pdf_path in enumerate(
        pdf_files,
        start=1
    ):

        try:

            text, page_count = extract_pdf(
                pdf_path
            )

            if not text.strip():

                print(
                    f"[WARNING] No text: "
                    f"{pdf_path.name}"
                )

            # ------------------------------------------------
            # Metadata available from folder structure
            # ------------------------------------------------

            year = pdf_path.parent.name

            # ------------------------------------------------
            # JSON structure
            # ------------------------------------------------

            result = {

                "source_file": pdf_path.name,

                "year": year,

                "pages": page_count,

                "text": text
            }

            # ------------------------------------------------
            # Output filename
            # ------------------------------------------------

            output_path = (
                OUTPUT_DIR /
                f"{pdf_path.stem}.json"
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            successful += 1

        except Exception as e:

            failed += 1

            print(
                f"[ERROR] {pdf_path.name}"
            )

            print(
                f"        {e}"
            )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if (
            index % 10 == 0
            or index == len(pdf_files)
        ):

            print(
                f"Processed "
                f"{index}/{len(pdf_files)}"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Output: {OUTPUT_DIR.resolve()}"
    )


if __name__ == "__main__":
    main()
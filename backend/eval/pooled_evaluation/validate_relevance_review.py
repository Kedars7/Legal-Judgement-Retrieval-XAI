
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = ROOT / "eval" / "pooled_evaluation" / "candidates_to_review.csv"
OUTPUT_PATH = ROOT / "eval" / "pooled_evaluation" / "candidates_to_review_working.csv"


def main():
    df = pd.read_csv(REVIEW_PATH)

    # Create editable judgment fields.
    if "relevance" not in df.columns:
        df["relevance"] = ""

    if "label_reason" not in df.columns:
        df["label_reason"] = ""

    # Keep review data separate from source artifacts.
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Review rows: {len(df)}")
    print(f"Working file: {OUTPUT_PATH}")
    print("\nRelevance instructions:")
    print("  1 = Substantively relevant to the query")
    print("  0 = Not substantively relevant to the query")
    print("Leave relevance blank until a human has reviewed the evidence.")


if __name__ == "__main__":
    main()

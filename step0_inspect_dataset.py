# Step 0: Inspect the job dataset to understand its columns, row count, and structure.

# Import pandas to easily read and display tabular data from CSV files.
import pandas as pd
# Import os to check if the dataset file exists before loading.
import os

def inspect_dataset(file_path="job_dataset.csv"):
    # Step 1: Check if the CSV file exists in the current directory.
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found in the current folder.")
        return

    # Step 2: Load the CSV file into a pandas DataFrame.
    # We use encoding="utf-8" with fallback to "latin-1" if needed.
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")

    # Step 3: Print the total number of rows (job postings) and columns.
    row_count, col_count = df.shape
    print("=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"Total number of rows (job postings): {row_count}")
    print(f"Total number of columns: {col_count}\n")

    # Step 4: Print all column names as a clean list.
    print("Column names:")
    for idx, col in enumerate(df.columns, start=1):
        print(f"  {idx}. {col}")
    print()

    # Step 5: Check whether there is a 'Skills' or description-related column.
    print("=" * 60)
    print("COLUMN CHECKS (Skills & Description)")
    print("=" * 60)
    has_skills = any("skill" in col.lower() for col in df.columns)
    has_description = any(
        any(term in col.lower() for term in ["description", "responsibilit", "detail", "summary"])
        for col in df.columns
    )

    if has_skills:
        skill_cols = [col for col in df.columns if "skill" in col.lower()]
        print(f"[FOUND] Skills column found: {skill_cols}")
    else:
        print("[MISSING] No dedicated 'Skills' column found.")

    if has_description:
        desc_cols = [
            col for col in df.columns
            if any(term in col.lower() for term in ["description", "responsibilit", "detail", "summary"])
        ]
        print(f"[FOUND] Description / Responsibilities column found: {desc_cols}")
    else:
        print("[MISSING] No job description/responsibilities column found.")
    print()

    # Step 6: Print 3 sample rows so we can inspect actual values.
    print("=" * 60)
    print("3 SAMPLE ROWS")
    print("=" * 60)
    # Loop over the first 3 rows and display each column and its value clearly.
    for i, row in df.head(3).iterrows():
        print(f"--- Sample Row {i + 1} ---")
        for col in df.columns:
            # Shorten very long text for clean terminal viewing
            val = str(row[col])
            if len(val) > 120:
                val = val[:117] + "..."
            print(f"  {col}: {val}")
        print()

if __name__ == "__main__":
    # Call the function to inspect job_dataset.csv
    inspect_dataset("job_dataset.csv")

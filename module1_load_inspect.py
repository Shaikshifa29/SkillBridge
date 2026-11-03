# Module 1: Load data and filter rows for AI/ML/Data roles.
# Written for beginner Python learners with clear, step-by-step comments.

# Import pandas to work with tabular data (rows and columns).
import pandas as pd

# Import Counter to count skill occurrences across job postings.
from collections import Counter

# Import os to check file paths.
import os


def load_dataset(file_path="job_dataset.csv"):
    """
    Step 1: Load the CSV dataset into a pandas DataFrame.
    """
    # Check if the dataset file exists in the directory.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file '{file_path}' was not found.")

    # Read the CSV file into a DataFrame using utf-8 encoding (fallback to latin-1 if needed).
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")

    # Return the loaded DataFrame.
    return df


def filter_ai_ml_data_roles(df):
    """
    Step 2: Filter the DataFrame for AI/ML/Data job roles using whole-word regex matching.
    """
    # Define a regex pattern using word boundaries (\b).
    # This matches whole words like 'AI', 'ML', 'Data', or multi-word phrases like
    # 'Artificial Intelligence' and 'Machine Learning'.
    # It prevents false matches where 'ai' appears inside words like 'Retail' or 'Trainee'.
    role_pattern = r"\b(?:AI|ML|Data)\b|Artificial Intelligence|Machine Learning"

    # Create a boolean True/False mask for each row where Title matches the pattern.
    # case=False makes the match case-insensitive (matches 'ai', 'Ai', 'AI', etc.).
    # na=False safely handles any missing or empty Title values.
    is_target_role = df["Title"].str.contains(
        role_pattern, case=False, na=False, regex=True
    )

    # Filter the original DataFrame to keep only the matching rows.
    # .copy() ensures we have an independent copy of the data.
    filtered_df = df[is_target_role].copy()

    # Return the filtered DataFrame.
    return filtered_df


def get_role_summary(filtered_df, total_original_rows):
    """
    Step 3: Return summary statistics about matched roles and experience levels.
    """
    # Count matched rows out of original dataset rows.
    matched_count = len(filtered_df)

    # Extract the 10 most common matched job titles as a dictionary.
    top_10_titles = filtered_df["Title"].value_counts().head(10).to_dict()

    # Extract the count of matched rows per ExperienceLevel as a dictionary.
    exp_counts = filtered_df["ExperienceLevel"].value_counts().to_dict()

    # Return the summary data dictionary instead of printing.
    return {
        "matched_count": matched_count,
        "total_original_rows": total_original_rows,
        "top_10_titles": top_10_titles,
        "experience_levels": exp_counts,
    }


# Backwards compatibility alias
print_role_summary = get_role_summary


def extract_skills_per_posting(filtered_df):
    """
    Step 4: Parse semicolon-separated skills: strip spaces, lowercase them,
    and count each skill at most once per job posting.
    """
    # Counter will store: {skill_name: number_of_postings_requiring_it}
    skill_counts = Counter()

    # Loop through each row's 'Skills' text in the filtered dataset.
    for skills_text in filtered_df["Skills"].dropna():
        # Step 4a: Split the string by semicolons (;).
        raw_skills = str(skills_text).split(";")

        # Step 4b: Clean each skill: strip leading/trailing whitespace and lowercase it.
        # Use a set comprehension so duplicate mentions in the SAME posting are counted only once.
        cleaned_posting_skills = {
            skill.strip().lower()
            for skill in raw_skills
            if skill.strip()
        }

        # Step 4c: Add 1 count for each unique skill present in this posting.
        skill_counts.update(cleaned_posting_skills)

    # Return the Counter dictionary containing all skill frequencies.
    return skill_counts


def run_module_1():
    """
    Main runner function for Module 1. Returns filtered data and skill counts.
    """
    # 1. Load the dataset.
    df = load_dataset("job_dataset.csv")

    # 2. Filter for AI/ML/Data roles using whole-word matching.
    ai_ml_data_jobs = filter_ai_ml_data_roles(df)

    # 3. Retrieve role summary data.
    summary = get_role_summary(ai_ml_data_jobs, len(df))

    # 4. Extract, clean, and count skills across the matched postings.
    skill_counts = extract_skills_per_posting(ai_ml_data_jobs)

    # Return the filtered jobs and skill counts data.
    return ai_ml_data_jobs, skill_counts


if __name__ == "__main__":
    # Execute Module 1 when run directly.
    run_module_1()

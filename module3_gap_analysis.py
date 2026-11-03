# Module 3: Skill Gap Analysis & Coverage Score
# Written for beginner Python learners with clear, step-by-step comments on every line.

# Import pandas to load and work with tabular data.
import pandas as pd

# Import re to handle regular expressions for cleaning text.
import re

# Import os to check file existence.
import os

# Import existing filtering and demand calculation logic from Module 2.
import module2_skill_demand as m2

# Step 1: Default hardcoded skills list for testing without typing.
# Contains:
# - Standard skills: 'Python', 'Pandas', 'Matplotlib'
# - Alias variations: 'sklearn' (maps to scikit-learn), 'mysql' (maps to sql), 'git/github' (maps to git)
# - Skills not in this dataset: 'LangChain', 'Quantum Computing'
DEFAULT_TEST_SKILLS = "Python, sklearn, mysql, Pandas, Matplotlib, git/github, Docker, LangChain, Quantum Computing"


def get_all_dataset_skills(file_path="job_dataset.csv"):
    """
    Step 2: Collect every unique valid skill present across the ENTIRE dataset.
    This lets us distinguish between:
    - Skills known to the dataset (even in other job roles)
    - Skills typed by the user that do not exist anywhere in the dataset
    """
    # Load dataset with fallback encoding.
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")

    # Set to store all unique skills in the dataset.
    dataset_skills = set()

    # Iterate through all non-null Skills rows in the entire dataset.
    for skills_text in df["Skills"].dropna():
        # Clean and extract skills using the exact same function as Module 2.
        posting_skills = m2.clean_and_extract_skills(skills_text)
        # Add them to our global set.
        dataset_skills.update(posting_skills)

    # Return the complete set of known dataset skills.
    return dataset_skills


def clean_user_skills(user_input_str):
    """
    Step 3: Clean and normalize user-typed skills using the EXACT same logic and
    alias dictionary as Module 2:
    - Lowercase and strip whitespace
    - Remove parenthetical text like '(advanced)'
    - Split compound skills like 'statistics: probability, linear algebra'
    - Replace aliases (sklearn -> scikit-learn, mysql -> sql, git/github -> git)
    - Deduplicate using a set
    """
    # Set to hold unique cleaned skills.
    cleaned_skills = set()

    # Split user input by commas (and semicolons if user used them).
    raw_tokens = re.split(r"[,;]", str(user_input_str))

    # Process each token entered by the user.
    for raw_token in raw_tokens:
        # Strip leading and trailing whitespace and convert to lowercase.
        token = raw_token.strip().lower()

        # Skip empty strings.
        if not token:
            continue

        # Check if user entered a compound skill with a colon (e.g., 'statistics: probability, linear algebra').
        if ":" in token:
            # Split into category prefix and items.
            category, items = token.split(":", 1)

            # Clean category name.
            cat_clean = re.sub(r"\(.*?\)", "", category).strip()
            if cat_clean and cat_clean not in ["tools", "frameworks", "libraries"]:
                # Apply alias mapping if available.
                canonical_cat = m2.SKILL_ALIASES.get(cat_clean, cat_clean)
                cleaned_skills.add(canonical_cat)

            # Split sub-items by comma.
            for sub_item in items.split(","):
                sub_clean = re.sub(r"\(.*?\)", "", sub_item).strip()
                if sub_clean:
                    canonical_sub = m2.SKILL_ALIASES.get(sub_clean, sub_clean)
                    cleaned_skills.add(canonical_sub)
        else:
            # Regular token: remove parenthetical notes like '(advanced)' or '(basics)'.
            token_clean = re.sub(r"\(.*?\)", "", token).strip()
            if token_clean:
                # Apply alias dictionary.
                canonical_token = m2.SKILL_ALIASES.get(token_clean, token_clean)
                cleaned_skills.add(canonical_token)

    # Return the deduplicated set of cleaned skills.
    return cleaned_skills


def perform_gap_analysis(user_skills, group_demand, all_dataset_skills, top_n=15):
    """
    Step 4: Perform the gap analysis comparing user skills against the target group demand:
    1. Skills I have (in top N)
    2. Skills I am missing (in top N, ordered by demand %)
    3. Coverage score (how many of top N user knows)
    4. Skills typed that are NOT anywhere in the dataset
    5. Additional skills user has that are in dataset but outside top N
    """
    # Extract top N target skills with rank, skill name, count, and demand percentage.
    top_target_skills = group_demand[:top_n]

    # Map for easy lookup: {skill_name: (rank, count, percentage)}
    top_skills_map = {
        item[0]: (idx + 1, item[1], item[2])
        for idx, item in enumerate(top_target_skills)
    }

    # Set of top N skill names.
    top_target_names = set(top_skills_map.keys())

    # 1. Skills user has that match top N skills.
    skills_matched_top = []
    for skill in top_target_skills:
        skill_name, count, pct = skill
        if skill_name in user_skills:
            rank = top_skills_map[skill_name][0]
            skills_matched_top.append((rank, skill_name, pct))

    # Deterministic sort: (-demand %, skill_name)
    skills_matched_top.sort(key=lambda item: (-item[2], item[1]))

    # 2. Skills in top N that the user is missing.
    skills_missing_top = []
    for skill in top_target_skills:
        skill_name, count, pct = skill
        if skill_name not in user_skills:
            rank = top_skills_map[skill_name][0]
            skills_missing_top.append((rank, skill_name, pct))

    # Deterministic sort: (-demand %, skill_name)
    skills_missing_top.sort(key=lambda item: (-item[2], item[1]))

    # 3. Coverage score calculation:
    matched_count = len(skills_matched_top)
    total_top = len(top_target_skills)
    coverage_percentage = (matched_count / total_top * 100.0) if total_top > 0 else 0.0

    # 4. User skills that do NOT appear anywhere in the entire dataset.
    skills_not_in_dataset = [
        skill for skill in sorted(user_skills)
        if skill not in all_dataset_skills
    ]

    # 5. User skills that ARE in dataset, but not in this group's top N.
    other_skills_user_has = [
        skill for skill in sorted(user_skills)
        if skill in all_dataset_skills and skill not in top_target_names
    ]

    # Return results in a structured dictionary.
    return {
        "matched_skills": skills_matched_top,
        "missing_skills": skills_missing_top,
        "matched_count": matched_count,
        "total_top": total_top,
        "coverage_percentage": coverage_percentage,
        "not_in_dataset": skills_not_in_dataset,
        "other_known_skills": other_skills_user_has,
    }


def get_gap_analysis_report(group_name, total_postings, user_skills, results):
    """
    Step 5: Return structured gap analysis data instead of printing.
    """
    # Return structured results dictionary
    return results


# Backwards compatibility alias
print_gap_analysis_report = get_gap_analysis_report


def run_module_3(user_skills_input=None, group_choice=None):
    """
    Step 6: Main runner function for Module 3.
    Accepts optional parameters and returns structured gap analysis results.
    """
    # 6a. Load dataset and target roles using Module 2 filter.
    all_kept_jobs = m2.load_and_filter_data("job_dataset.csv")

    # 6b. Collect all unique skills across the entire dataset.
    all_dataset_skills = get_all_dataset_skills("job_dataset.csv")

    # 6c. Handle group choice:
    # 1 or "All Roles" = All Roles (N=47)
    # 2 or "Fresher Only" = Fresher Only (N=14)
    if group_choice is None:
        group_choice = "2"

    if str(group_choice) in ["1", "All Roles"]:
        target_group = all_kept_jobs
        group_name = "All Kept Roles"
    else:
        fresher_mask = all_kept_jobs["ExperienceLevel"] == "Fresher"
        target_group = all_kept_jobs[fresher_mask]
        group_name = "Fresher Only"

    # 6d. Calculate demand for the selected group.
    group_demand = m2.calculate_skill_demand(target_group)

    # 6e. Handle user skills input:
    # Do NOT fall back to hardcoded default test skills. If empty, clean_user_skills returns set().
    if user_skills_input is None:
        user_skills_input = ""

    # 6f. Clean and normalize user skills using the exact same pipeline and aliases.
    cleaned_user_skills = clean_user_skills(user_skills_input)

    # 6g. Perform gap analysis.
    results = perform_gap_analysis(
        cleaned_user_skills, group_demand, all_dataset_skills, top_n=15
    )

    # Attach group metadata to results so Module 4 uses the EXACT same group and demand table
    results["group_choice"] = group_choice
    results["group_name"] = group_name
    results["total_postings"] = len(target_group)
    results["group_demand"] = group_demand
    results["demand_dict"] = {item[0]: item[2] for item in group_demand}
    results["cleaned_user_skills"] = cleaned_user_skills

    # Return results dictionary instead of printing
    return results


if __name__ == "__main__":
    # Execute Module 3 with default test skills when run directly from CLI.
    run_module_3(DEFAULT_TEST_SKILLS)

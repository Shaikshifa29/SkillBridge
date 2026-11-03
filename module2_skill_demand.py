# Module 2: Skill Demand Analysis with Skill Normalization & Aliases
# Written for beginner Python learners with clear, step-by-step comments.

# Import pandas to load and filter tabular data.
import pandas as pd

# Import Counter to count frequency of each skill.
from collections import Counter

# Import re to handle compound string patterns.
import re

# Import os to verify file paths.
import os

# Import matplotlib to generate bar chart graphics without requiring a display server.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Step 3 requirement: Define a small alias dictionary to normalize common variations.
SKILL_ALIASES = {
    "sklearn": "scikit-learn",
    "mysql": "sql",
    "postgresql": "sql",
    "postgres": "sql",
    "git/github": "git",
    "github": "git",
}


def load_and_filter_data(file_path="job_dataset.csv"):
    """
    Step 1: Load the dataset and filter for targeted AI, ML, and Data Science roles.
    Excludes Prompt, Big Data, Data Engineer, and Data Analyst roles.
    """
    # Verify file exists.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    # Load dataset with fallback encoding.
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")

    # Positive pattern: keep AI Engineer, Machine Learning, ML, Data Scientist, or Data Science.
    include_pattern = r"AI Engineer|Machine Learning|\bML\b|Data Scientist|Data Science"

    # Negative pattern: exclude Prompt, Big Data, Data Engineer, and Data Analyst.
    exclude_pattern = r"Prompt|Big Data|Data Engineer|Data Analyst"

    # Create boolean filter mask.
    is_included = df["Title"].str.contains(include_pattern, case=False, na=False, regex=True)
    is_excluded = df["Title"].str.contains(exclude_pattern, case=False, na=False, regex=True)
    target_mask = is_included & (~is_excluded)

    # Kept job postings.
    all_kept_jobs = df[target_mask].copy()

    # Return the kept DataFrame.
    return all_kept_jobs


def clean_and_extract_skills(skills_text):
    """
    Step 2: Clean and normalize skills from a single posting:
    - Semicolon-separated tokenization (exact token matching)
    - Lowercase and strip whitespace
    - Split compound skills (e.g. 'statistics: probability, linear algebra')
    - Map aliases (sklearn -> scikit-learn, mysql/postgresql -> sql, git/github -> git)
    - Deduplicate per posting using a set
    """
    cleaned_skills = set()

    # Split on semicolons to get individual skill tokens.
    raw_tokens = str(skills_text).split(";")

    for raw_token in raw_tokens:
        token = raw_token.strip().lower()
        if not token:
            continue

        # If token contains a colon ':', it is a compound skill (e.g. 'category: item1, item2')
        if ":" in token:
            category, items = token.split(":", 1)

            # Clean and add the category prefix itself (e.g. 'statistics')
            cat_clean = re.sub(r"\(.*?\)", "", category).strip()
            if cat_clean:
                canonical_cat = SKILL_ALIASES.get(cat_clean, cat_clean)
                cleaned_skills.add(canonical_cat)

            # Split sub-items by comma (e.g. 'probability', 'linear algebra')
            for sub_item in items.split(","):
                sub_clean = re.sub(r"\(.*?\)", "", sub_item).strip()
                if sub_clean:
                    canonical_sub = SKILL_ALIASES.get(sub_clean, sub_clean)
                    cleaned_skills.add(canonical_sub)
        else:
            # Regular token without colon: remove parenthetical notes like '(advanced)'
            token_clean = re.sub(r"\(.*?\)", "", token).strip()
            if token_clean:
                canonical_token = SKILL_ALIASES.get(token_clean, token_clean)
                cleaned_skills.add(canonical_token)

    return cleaned_skills


def calculate_skill_demand(jobs_df):
    """
    Step 3: Calculate percentage demand for every unique skill.
    Demand % = (postings requiring the skill / total postings in subset) * 100.
    """
    skill_counter = Counter()
    total_postings = len(jobs_df)

    if total_postings == 0:
        return []

    # Process each posting's skills string using our clean_and_extract_skills function.
    for skills_text in jobs_df["Skills"].dropna():
        unique_posting_skills = clean_and_extract_skills(skills_text)
        skill_counter.update(unique_posting_skills)

    # Compute percentages and sort deterministically.
    skill_demand_list = []
    for skill, count in skill_counter.items():
        percentage = (count / total_postings) * 100.0
        skill_demand_list.append((skill, count, percentage))

    # Deterministic sort: Primary key is demand % descending (-item[2]),
    # with ties broken alphabetically by skill name (item[0]).
    skill_demand_list.sort(key=lambda item: (-item[2], item[0]))
    return skill_demand_list


def get_side_by_side_comparison(all_demand, sub_demand, total_all, total_sub, sub_label):
    """
    Step 4: Return the top 15 skills side-by-side comparison data instead of printing.
    """
    top_15_all = all_demand[:15]
    top_15_sub = sub_demand[:15]
    comparison_table = []

    for i in range(15):
        rank = i + 1
        skill_all = top_15_all[i] if i < len(top_15_all) else None
        skill_sub = top_15_sub[i] if i < len(top_15_sub) else None
        comparison_table.append({
            "rank": rank,
            "all_roles": skill_all,
            "sub_group": skill_sub,
        })

    return comparison_table


# Backwards compatibility alias
print_side_by_side_comparison = get_side_by_side_comparison


def plot_skill_demand_chart(all_demand, sub_demand, total_all, total_sub, sub_title, output_file="skill_demand.png"):
    """
    Step 5: Create a 2-panel horizontal bar chart comparing All Roles vs the Subset,
    labeling bars with percentages and saving as skill_demand.png.
    """
    top_all = all_demand[:15]
    top_sub = sub_demand[:15]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # --- Plot 1: All Kept Roles ---
    skills_1 = [item[0] for item in reversed(top_all)]
    percentages_1 = [item[2] for item in reversed(top_all)]

    bars1 = ax1.barh(skills_1, percentages_1, color="#2980b9", edgecolor="#1c5980", height=0.65)
    ax1.set_title(f"Top 15 Skills - All Kept Roles (N={total_all})", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Demand Percentage (%)", fontsize=11)
    ax1.set_xlim(0, 115)

    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", ha="left", fontsize=9)

    # --- Plot 2: Subset (Fresher or Early-Career) ---
    skills_2 = [item[0] for item in reversed(top_sub)]
    percentages_2 = [item[2] for item in reversed(top_sub)]

    bars2 = ax2.barh(skills_2, percentages_2, color="#27ae60", edgecolor="#1e8449", height=0.65)
    ax2.set_title(sub_title, fontsize=12, fontweight="bold")
    ax2.set_xlabel("Demand Percentage (%)", fontsize=11)
    ax2.set_xlim(0, 115)

    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", ha="left", fontsize=9)

    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    # Return output file path instead of printing
    return output_file


def run_module_2():
    """
    Main runner for Module 2. Returns all_demand and sub_demand data.
    """
    # 1. Load kept jobs.
    all_kept_jobs = load_and_filter_data("job_dataset.csv")

    # 2. Determine ExperienceLevel breakdown.
    fresher_mask = all_kept_jobs["ExperienceLevel"] == "Fresher"
    junior_mask = all_kept_jobs["ExperienceLevel"].isin(["Junior", "Entry-Level"])
    fresher_junior_count = (fresher_mask | junior_mask).sum()
    fresher_only_count = fresher_mask.sum()

    # Requirement 4 check:
    # If Fresher + Junior has 25+ rows, use 'early-career'. Otherwise keep Fresher only and label "indicative, small sample".
    if fresher_junior_count >= 25:
        sub_group = all_kept_jobs[fresher_mask | junior_mask].copy()
        sub_label = "Early-Career (Fresher+Junior)"
        sub_title = f"Top 15 Skills - Early-Career Group (N={len(sub_group)})"
    else:
        sub_group = all_kept_jobs[fresher_mask].copy()
        sub_label = "Fresher Only"
        sub_title = f"Top 15 Skills - Fresher Only (N={len(sub_group)})\n[indicative, small sample]"

    # 3. Calculate skill demand for both sets.
    all_demand = calculate_skill_demand(all_kept_jobs)
    sub_demand = calculate_skill_demand(sub_group)

    # 4. Generate comparison data.
    comparison = get_side_by_side_comparison(
        all_demand, sub_demand, len(all_kept_jobs), len(sub_group), sub_label
    )

    # 5. Plot and save chart.
    plot_skill_demand_chart(
        all_demand, sub_demand, len(all_kept_jobs), len(sub_group), sub_title, output_file="skill_demand.png"
    )

    # Return data instead of printing.
    return all_demand, sub_demand


if __name__ == "__main__":
    run_module_2()

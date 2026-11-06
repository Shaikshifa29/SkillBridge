# Module 4: Learning Roadmap Generator with Prerequisites & Free Resources
# Written for beginner Python learners with clear, step-by-step comments on every line.

# Import sys to handle system path and arguments if needed.
import sys

# Import os to check file paths.
import os

# Import urllib.parse to handle URL encoding for search fallback queries.
import urllib.parse

# Import Module 2 and Module 3 to reuse data loading, filtering, demand calculation, and gap analysis.
import module2_skill_demand as m2
import module3_gap_analysis as m3


# Step 0: Verification function for "r" in kept roles.
# Verifies that 'r' is matched as an exact semicolon-separated token in the 47 kept rows
# and displays 3 raw Skills strings containing it.
def verify_r_token():
    """
    Step 0: Verification of 'r' exact token matching in the 47 kept rows.
    Returns verification dictionary instead of printing.
    """
    # Load the 47 kept roles using Module 2's filter.
    all_kept_jobs = m2.load_and_filter_data("job_dataset.csv")

    # Collect all job postings that contain 'r' as an exact token.
    r_matches = []
    for raw_skills in all_kept_jobs["Skills"].dropna():
        # Split string strictly by semicolons and strip/lowercase each token.
        tokens = [token.strip().lower() for token in str(raw_skills).split(";")]
        if "r" in tokens:
            r_matches.append(str(raw_skills))

    total_kept = len(all_kept_jobs)
    count_r = len(r_matches)
    percentage_r = (count_r / total_kept) * 100.0 if total_kept > 0 else 0.0

    # Return structured verification result
    return {
        "total_kept": total_kept,
        "count_r": count_r,
        "percentage_r": percentage_r,
        "sample_strings": r_matches[:3],
    }


# Backwards compatibility alias
print_r_token_verification = verify_r_token


# Step 1: Hand-written prerequisite dictionary.
# Key: The advanced/target skill.
# Value: List of foundational prerequisite skills that must be learned BEFORE it.
# Skills with an empty list [] are foundational entry points with no prior dependencies.
PREREQUISITES = {
    # Foundational Programming & Query Languages (Entry points - No prerequisites)
    "python": [],
    "r": [],
    "sql": [],
    "java": [],
    "c++": [],
    "git": [],

    # Data Manipulation & Visualization
    "numpy": ["python"],
    "pandas": ["python", "numpy"],
    "matplotlib": ["python"],
    "seaborn": ["matplotlib", "pandas"],

    # Data Preparation & Feature Engineering
    "data preprocessing": ["pandas", "numpy"],
    "feature engineering": ["data preprocessing", "pandas"],

    # Machine Learning Core Foundations
    "basic ml": ["python", "numpy", "pandas"],
    "regression": ["basic ml"],
    "classification": ["basic ml"],
    "decision trees": ["classification"],
    "clustering": ["basic ml"],
    "scikit-learn": ["basic ml", "pandas"],

    # Deep Learning & Advanced Artificial Intelligence
    "deep learning": ["scikit-learn"],
    "neural networks": ["deep learning"],
    "tensorflow": ["deep learning"],
    "pytorch": ["deep learning"],
    "keras": ["tensorflow"],
    "computer vision": ["deep learning", "numpy"],
    "nlp": ["scikit-learn", "deep learning"],
    "reinforcement learning": ["deep learning", "numpy"],

    # Big Data & Distributed Computing
    "hadoop": ["java"],
    "spark": ["python", "sql", "hadoop"],
}


import career_roles

# Master learning resources dictionary mapping skill -> (title, url)
# Merges career roles master verified resources with base resources
RESOURCES = {**career_roles.LEARNING_RESOURCES}

# Backwards compatibility dictionary containing just resource titles
FREE_RESOURCES = {skill: title for skill, (title, url) in RESOURCES.items()}

# Module-level exports declaration
__all__ = [
    "RESOURCES",
    "FREE_RESOURCES",
    "get_skill_resource",
    "generate_roadmap_from_gap",
    "run_module_4",
    "build_learning_roadmap",
    "expand_with_unmet_prerequisites",
]


def get_skill_resource(skill_name):
    """
    Look up learning resource (title, url) for a skill from career_roles repository.
    Returns verified, authoritative clickable link for each specific topic.
    """
    return career_roles.get_skill_resource(skill_name)


# Change 1: Set of optional / specialized skills (alternative language & Big Data stack).
# These skills are moved into an [Optional] group printed after the main roadmap,
# ordered by market demand percentage.
OPTIONAL_SKILLS = {"r", "java", "hadoop", "spark"}


def expand_with_unmet_prerequisites(missing_skills, user_known_skills, prerequisites_dict):
    """
    Step 3: Collect all missing skills plus any unmet prerequisites recursively.
    Even if a prerequisite skill wasn't in the Top 15 list, this ensures it is
    included in the learning path before the skill that depends on it.
    """
    # Start with the missing skills identified in Module 3.
    skills_to_learn = set(missing_skills)

    # Set of skills the user already knows.
    known = set(user_known_skills)

    # Track which skills were added purely as prerequisite requirements.
    unmet_prerequisites_added = set()

    # Loop repeatedly until all dependencies are resolved.
    expanded = True
    while expanded:
        expanded = False
        current_list = list(skills_to_learn)
        for skill in current_list:
            # Check what this skill requires.
            prereqs = prerequisites_dict.get(skill, [])
            for prereq in prereqs:
                # If user doesn't already know this prereq and it's not yet in our study list:
                if prereq not in known and prereq not in skills_to_learn:
                    skills_to_learn.add(prereq)
                    unmet_prerequisites_added.add(prereq)
                    # Set expanded to True so we also check prereqs of this newly added prereq!
                    expanded = True

    return skills_to_learn, unmet_prerequisites_added


def build_learning_roadmap(skills_to_learn, unmet_prereqs_added, demand_dict, prerequisites_dict):
    """
    Step 4: Sort skills into numbered learning steps:
    1. Prerequisites ALWAYS come first (Topological Ordering using Kahn's Algorithm).
    2. Ties among concurrently available skills are broken by Market Demand % (highest first).
    3. Change 2: Separate hadoop, spark, java, and r into an [Optional] group
       printed after the main roadmap, ordered by market demand %.
    """
    # in_degree stores: how many unmet prerequisite skills still need to be completed
    # before this skill can be studied.
    in_degree = {skill: 0 for skill in sorted(skills_to_learn)}

    # dependents stores: which skills are unlocked when this skill is completed.
    dependents = {skill: [] for skill in sorted(skills_to_learn)}

    # Populate in-degree and dependents graph deterministically.
    for skill in sorted(skills_to_learn):
        for prereq in prerequisites_dict.get(skill, []):
            # Only count prerequisites that are currently in our learning set.
            if prereq in skills_to_learn:
                in_degree[skill] += 1
                dependents[prereq].append(skill)

    # Ready queue: skills with in_degree == 0 (all prerequisites are satisfied).
    ready = [skill for skill in sorted(skills_to_learn) if in_degree[skill] == 0]

    # Full topologically sorted list.
    full_roadmap = []

    # Process skills step by step using Kahn's topological sort algorithm.
    while ready:
        # Sort ready skills:
        # Primary key: Market Demand % descending (-demand_dict.get(skill, 0.0))
        # Secondary key: Alphabetical skill name (to guarantee consistent ordering)
        ready.sort(key=lambda s: (-demand_dict.get(s, 0.0), s))

        # Select the ready skill with the highest market demand.
        next_skill = ready.pop(0)

        # Record whether this skill was added as an unmet prerequisite.
        is_prereq = next_skill in unmet_prereqs_added

        # Fetch free learning resource title and direct URL.
        resource_title, resource_url = get_skill_resource(next_skill)

        # Add this step to our roadmap list.
        full_roadmap.append({
            "skill": next_skill,
            "demand_pct": demand_dict.get(next_skill, 0.0),
            "is_unmet_prereq": is_prereq,
            "resource": resource_title,
            "resource_title": resource_title,
            "resource_url": resource_url,
            "tag": "[Prerequisite Added]" if is_prereq else "[Top 15 Missing]",
        })

        # Decrement in_degree for all skills waiting on this completed skill.
        for dependent_skill in dependents[next_skill]:
            in_degree[dependent_skill] -= 1
            # If all prerequisites are now satisfied, add to the ready list!
            if in_degree[dependent_skill] == 0:
                ready.append(dependent_skill)

    # Change 3: Partition skills into:
    # (a) main_roadmap (Core AI/ML & Data Science Track - required)
    # (b) optional_roadmap (hadoop, spark, java, r - alternative languages & Big Data)
    main_roadmap = []
    optional_roadmap = []

    for item in full_roadmap:
        if item["skill"] in OPTIONAL_SKILLS:
            # Mark label as [Optional]
            item["tag"] = "[Optional]"
            optional_roadmap.append(item)
        else:
            main_roadmap.append(item)

    # Change 4: Order the optional group strictly by Market Demand % descending.
    optional_roadmap.sort(key=lambda item: (-item["demand_pct"], item["skill"]))

    return main_roadmap, optional_roadmap


def get_roadmap_report(group_name, total_postings, main_roadmap, optional_roadmap, unmet_prereqs_added):
    """
    Step 5: Return structured roadmap report data instead of printing.
    """
    return {
        "group_name": group_name,
        "total_postings": total_postings,
        "main_roadmap": main_roadmap,
        "optional_roadmap": optional_roadmap,
        "unmet_prereqs_added": unmet_prereqs_added,
    }


# Backwards compatibility alias
print_roadmap_report = get_roadmap_report


def generate_roadmap_from_gap(gap_results):
    """
    Helper function: Generate roadmap directly from existing gap analysis results.
    """
    demand_dict = gap_results["demand_dict"]
    user_known_skills = set(gap_results["cleaned_user_skills"])
    missing_top_skills = [item[1] for item in gap_results["missing_skills"]]

    # Expand with unmet prerequisites
    skills_to_learn, unmet_prereqs_added = expand_with_unmet_prerequisites(
        missing_top_skills, user_known_skills, PREREQUISITES
    )

    # Build partitioned learning roadmap
    main_roadmap, optional_roadmap = build_learning_roadmap(
        skills_to_learn, unmet_prereqs_added, demand_dict, PREREQUISITES
    )

    return main_roadmap, optional_roadmap, unmet_prereqs_added


def run_module_4(user_skills_input=None, group_choice=None):
    """
    Step 6: Main runner for Module 4.
    Runs verification, invokes Module 3, and builds the partitioned learning roadmap.
    Returns main_roadmap and optional_roadmap data instead of printing.
    """
    # 6a. Step 0: Verify 'r' exact token matching in 47 kept rows.
    r_verification = verify_r_token()

    # 6b. Run Module 3 to perform gap analysis.
    gap_results = m3.run_module_3(
        user_skills_input=user_skills_input, group_choice=group_choice
    )

    # 6c. Build the partitioned learning roadmap: main track + optional track.
    main_roadmap, optional_roadmap, unmet_prereqs_added = generate_roadmap_from_gap(gap_results)

    # Return roadmap data instead of printing.
    return main_roadmap, optional_roadmap


if __name__ == "__main__":
    # Execute Module 4 when run directly.
    run_module_4()

# planner.py - Rule-Based Study Planner & Assistant Backend
# Contains approximate study hours, deterministic schedule generation, and keyword-based assistant logic.
# Strict requirement: NO Streamlit code inside this backend module.

import datetime
import math
import re
import urllib.parse

# Import module4_roadmap to access learning resources
import module4_roadmap as m4


# -----------------------------------------------------------------------------
# 1. APPROXIMATE STUDY HOURS PER SKILL
# Note: These are hand-written rough estimates of hours required to learn
# the fundamental concepts of each skill for a motivated beginner/intermediate.
# -----------------------------------------------------------------------------
HOURS = {
    # Core Programming & Data Handling
    "python": 15,
    "numpy": 8,
    "pandas": 10,
    "sql": 12,

    # Classical Machine Learning
    "scikit-learn": 20,
    "basic ml": 15,
    "classification": 10,
    "regression": 10,
    "clustering": 8,
    "decision trees": 8,
    "data preprocessing": 10,
    "feature engineering": 12,

    # Deep Learning & Modern AI
    "deep learning": 25,
    "pytorch": 20,
    "tensorflow": 20,
    "keras": 10,
    "nlp": 15,
    "neural networks": 15,
    "computer vision": 20,
    "reinforcement learning": 25,

    # Data Visualization & Tooling
    "matplotlib": 6,
    "seaborn": 6,
    "git": 6,
    "docker": 10,

    # Big Data & Alternative Languages
    "java": 20,
    "hadoop": 15,
    "spark": 15,
    "r": 15,
    "c++": 25,

    # Cloud & Deployment
    "aws": 15,
    "azure": 15,
    "gcp": 15,
    "ci/cd": 10,
    "powerbi": 10,
    "tableau": 10,
    "mongodb": 10,
    "nosql": 10,
}

# Fallback hours for any unrecognized or niche skill
DEFAULT_HOURS = 10


# -----------------------------------------------------------------------------
# 2. ONE-LINE SKILL DESCRIPTIONS
# Accurate, informative descriptions for "what is <skill>" queries.
# -----------------------------------------------------------------------------
SKILL_DESCRIPTIONS = {
    "python": "High-level programming language essential for data manipulation, AI development, and automation.",
    "numpy": "Fundamental Python library for high-performance numerical computing and multi-dimensional array operations.",
    "pandas": "Core data manipulation and analysis library offering DataFrame structures for tabular data processing.",
    "sql": "Standard query language used to extract, filter, join, and manage data within relational databases.",
    "scikit-learn": "Industry-standard machine learning library providing algorithms for classification, regression, and clustering.",
    "basic ml": "Foundational machine learning concepts including model training, validation splits, loss functions, and bias-variance tradeoff.",
    "classification": "Supervised learning technique where models predict discrete categorical class labels for given inputs.",
    "regression": "Supervised learning method used to predict continuous numerical targets from input features.",
    "clustering": "Unsupervised learning algorithm that groups similar, unlabelled data points into cohesive clusters (e.g. K-Means).",
    "decision trees": "Intuitive tree-structured supervised models that make sequential decisions based on feature thresholds.",
    "data preprocessing": "Techniques for cleaning raw datasets, handling missing values, standardizing scales, and encoding categorical variables.",
    "feature engineering": "The process of extracting, transforming, and combining raw variables to maximize machine learning model accuracy.",
    "deep learning": "Advanced subfield of machine learning based on multi-layered artificial neural networks capable of learning complex representations.",
    "pytorch": "Dynamic open-source deep learning framework widely used in research and industry for computer vision and NLP.",
    "tensorflow": "Google's production-grade end-to-end open-source platform for training and deploying deep learning models at scale.",
    "keras": "User-friendly high-level neural networks API built on TensorFlow designed for rapid experimentation.",
    "nlp": "Natural Language Processing algorithms that enable computers to understand, parse, and generate human language text.",
    "matplotlib": "Versatile 2D plotting library for creating publication-quality charts and static figures in Python.",
    "seaborn": "Statistical visualization library built on Matplotlib that produces elegant, informative statistical graphics.",
    "git": "Distributed version control system essential for tracking code changes, branching, and team collaboration.",
    "docker": "Containerization platform that packages applications and dependencies into standardized, isolated containers.",
    "java": "Robust, object-oriented programming language extensively used in enterprise software and distributed Big Data backends.",
    "hadoop": "Distributed storage and processing framework (HDFS & MapReduce) built to handle massive data volumes across clusters.",
    "spark": "Lightning-fast distributed computing engine for in-memory large-scale data processing and analytics.",
    "r": "Statistical programming language and environment tailored specifically for data exploration, biostatistics, and graphing.",
    "c++": "High-performance compiled language commonly used for low-level system optimization, computer vision, and game engines.",
    "aws": "Amazon Web Services, the leading cloud computing platform offering scalable computing, storage, and AI infrastructure.",
    "azure": "Microsoft's enterprise cloud computing platform providing robust AI, data warehousing, and infrastructure services.",
    "gcp": "Google Cloud Platform, offering premier infrastructure for BigQuery, data analytics, and machine learning models.",
    "powerbi": "Microsoft's business analytics service providing interactive visualizations and business intelligence reporting.",
    "tableau": "Interactive data visualization and business analytics tool used to turn raw data into actionable dashboards.",
    "mongodb": "Leading NoSQL document-oriented database designed for high availability, scalability, and JSON-like schemas.",
    "nosql": "Non-relational database architecture optimized for unstructured, semi-structured, and distributed data storage.",
}


# -----------------------------------------------------------------------------
# 3. SCHEDULE GENERATION
# make_schedule(roadmap_steps, hours_per_day, days_per_week, start_date)
# Fills each day's hours in roadmap order, returning weeks with tasks like
# "Mon 4 Nov: numpy (2h)" and the total weeks needed.
# -----------------------------------------------------------------------------
def make_schedule(roadmap_steps, hours_per_day, days_per_week, start_date):
    """
    Generate a deterministic study schedule across weeks.
    
    Parameters:
    - roadmap_steps: list of dicts (with 'skill' key) or list of skill strings.
    - hours_per_day: int or float (1 to 6).
    - days_per_week: int (3 to 7).
    - start_date: datetime.date, datetime.datetime, or ISO string.
    
    Returns:
    - weeks: list of dicts with week number, date range, and daily tasks.
    - total_weeks: int (total number of calendar weeks needed).
    """
    # Normalize start_date
    if isinstance(start_date, str):
        start_date = datetime.date.fromisoformat(start_date)
    elif isinstance(start_date, datetime.datetime):
        start_date = start_date.date()

    # Determine which weekdays are study days (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun)
    if days_per_week >= 7:
        study_weekdays = {0, 1, 2, 3, 4, 5, 6}
    elif days_per_week == 6:
        study_weekdays = {0, 1, 2, 3, 4, 5}
    elif days_per_week == 5:
        study_weekdays = {0, 1, 2, 3, 4}
    elif days_per_week == 4:
        study_weekdays = {0, 1, 2, 3}
    elif days_per_week == 3:
        study_weekdays = {0, 2, 4}  # Mon, Wed, Fri
    else:
        study_weekdays = set(range(max(1, days_per_week)))

    # Build queue of skills with required hours in exact roadmap order
    task_queue = []
    for item in roadmap_steps:
        skill_name = item["skill"] if isinstance(item, dict) else str(item)
        clean_skill = skill_name.strip().lower()
        allocated_hours = HOURS.get(clean_skill, DEFAULT_HOURS)
        task_queue.append({
            "skill": clean_skill,
            "display_name": clean_skill,
            "remaining_hours": float(allocated_hours),
            "total_hours": float(allocated_hours),
        })

    weeks = []
    current_week_days = []
    current_week_num = 1
    current_date = start_date

    # Fill daily capacity in roadmap order
    while any(task["remaining_hours"] > 0 for task in task_queue):
        # Calculate calendar week index relative to start_date
        days_elapsed = (current_date - start_date).days
        week_idx = (days_elapsed // 7) + 1

        # When moving into a new week, record the previous week
        if week_idx > current_week_num:
            if current_week_days:
                weeks.append({
                    "week_num": current_week_num,
                    "label": f"Week {current_week_num}",
                    "days": current_week_days,
                })
                current_week_days = []
            current_week_num = week_idx

        # Check if today is a scheduled study day
        if current_date.weekday() in study_weekdays:
            daily_hours_left = float(hours_per_day)
            day_allocations = []

            for task in task_queue:
                if task["remaining_hours"] <= 0:
                    continue

                # Allocate hours to this skill
                chunk = min(daily_hours_left, task["remaining_hours"])
                task["remaining_hours"] -= chunk
                daily_hours_left -= chunk

                chunk_str = f"{int(chunk)}h" if chunk == int(chunk) else f"{chunk:.1f}h"
                day_allocations.append(f"{task['skill']} ({chunk_str})")

                if daily_hours_left <= 0:
                    break

            if day_allocations:
                # Format: "Mon 4 Nov: numpy (2h)"
                date_str = f"{current_date.strftime('%a')} {current_date.day} {current_date.strftime('%b')}"
                tasks_text = ", ".join(day_allocations)
                full_entry = f"{date_str}: {tasks_text}"
                current_week_days.append({
                    "date": current_date,
                    "date_str": date_str,
                    "tasks_str": tasks_text,
                    "entry": full_entry,
                })

        # Advance to the next calendar day
        current_date += datetime.timedelta(days=1)

    # Append any remaining days in the last week
    if current_week_days:
        weeks.append({
            "week_num": current_week_num,
            "label": f"Week {current_week_num}",
            "days": current_week_days,
        })

    total_weeks = len(weeks)
    return weeks, total_weeks


# -----------------------------------------------------------------------------
# 4. RULE-BASED STUDY ASSISTANT (Keyword Matching)
# Keyword matching on the user's latest analysis in st.session_state.
# -----------------------------------------------------------------------------
def get_study_assistant_response(query, analysis_results, schedule_context=None):
    """
    Generate rule-based answers to study questions based on analysis_results.
    
    Parameters:
    - query: str, user question.
    - analysis_results: dict from st.session_state["analysis_results"], or None.
    - schedule_context: tuple (weeks, total_weeks, hours_per_day, days_per_week) or None.
    
    Returns:
    - str response.
    """
    # Guard: If no analysis exists, return exact specified message
    if not analysis_results:
        return "Click Analyze first."

    if not query or not query.strip():
        return "How can I help you with your learning roadmap? Ask me what to learn first, why a skill was chosen, or how long your plan will take."

    q = query.strip().lower()

    # Extract roadmap and gap analysis components
    gap_results = analysis_results.get("gap_results", {})
    main_roadmap = analysis_results.get("main_roadmap", [])
    optional_roadmap = analysis_results.get("optional_roadmap", [])
    all_roadmap_items = main_roadmap + optional_roadmap
    group_name = analysis_results.get("group_name", "Target Group")

    # -------------------------------------------------------------------------
    # Case 1: "what first" / "what next"
    # -------------------------------------------------------------------------
    if any(k in q for k in ["what first", "first step", "learn first", "start with", "what next", "where to start", "where do i start", "what's next"]):
        if main_roadmap:
            first_step = main_roadmap[0]
            skill_name = first_step["skill"]
            demand = first_step.get("demand_pct", 0.0)
            is_prereq = first_step.get("is_unmet_prereq", False)

            if is_prereq:
                reason = f"It was added as an essential prerequisite that unlocks subsequent algorithms in your curriculum (Market Demand: {demand:.1f}%)."
            else:
                reason = f"It has the highest market demand ({demand:.1f}%) among your unmastered core skills."

            res_title, res_url = m4.get_skill_resource(skill_name)
            return (
                f"🎯 **Start with {skill_name.title()}!**\n\n"
                f"**Why this first?** {reason}\n\n"
                f"📖 Free Resource: [{res_title}]({res_url})"
            )
        else:
            return "🎉 You have mastered all core skills in this track! You can proceed to explore optional specialized technologies."

    # -------------------------------------------------------------------------
    # Case 2: "why <skill>"
    # -------------------------------------------------------------------------
    if q.startswith("why ") or "why should i learn" in q or "why is" in q or "why do i need" in q or "reason for" in q:
        # Find which skill is mentioned in the query
        found_item = None
        for item in all_roadmap_items:
            if item["skill"].lower() in q:
                found_item = item
                break

        # Also check matched skills (already known)
        if not found_item and gap_results.get("matched_skills"):
            for rank, matched_s, pct in gap_results["matched_skills"]:
                if matched_s.lower() in q:
                    return f"💡 **{matched_s.title()}** is already in your skill profile! You have mastered it, so it is omitted from your learning roadmap."

        if found_item:
            skill_name = found_item["skill"]
            demand = found_item.get("demand_pct", 0.0)
            is_prereq = found_item.get("is_unmet_prereq", False)

            if is_prereq:
                # Look up dependents in PREREQUISITES
                dependents = [
                    parent for parent, reqs in m4.PREREQUISITES.items()
                    if skill_name in reqs
                ]
                dep_str = ", ".join(d.title() for d in dependents[:3]) if dependents else "advanced ML libraries"
                return (
                    f"💡 **Why learn {skill_name.title()}?**\n\n"
                    f"**Prerequisite reason:** {skill_name.title()} is a fundamental building block required before studying **{dep_str}**. "
                    f"Additionally, it holds a **{demand:.1f}% market demand** across {group_name} job postings."
                )
            else:
                return (
                    f"📈 **Why learn {skill_name.title()}?**\n\n"
                    f"**Market Demand:** {skill_name.title()} appears in **{demand:.1f}%** of target job postings for **{group_name}**, "
                    f"making it a high-impact core capability for data science and AI roles."
                )
        else:
            return (
                "Please specify a skill from your roadmap to understand why it was selected. "
                "For example: *'Why numpy?'* or *'Why scikit-learn?'*"
            )

    # -------------------------------------------------------------------------
    # Case 3: "how long" / "weeks" / "hours" / "time"
    # -------------------------------------------------------------------------
    if any(k in q for k in ["how long", "how many weeks", "weeks", "duration", "how much time", "total hours", "time estimate"]):
        total_hours = sum(HOURS.get(item["skill"].lower().strip(), DEFAULT_HOURS) for item in all_roadmap_items)
        skill_count = len(all_roadmap_items)

        if schedule_context:
            weeks_list, total_weeks, h_day, d_week = schedule_context
            return (
                f"⏱️ **Roadmap Duration Estimate:**\n\n"
                f"• Total curriculum: **{total_hours} study hours** across **{skill_count} skills**.\n"
                f"• At your current pace of **{h_day} hours/day** for **{d_week} days/week** ({h_day * d_week}h/week):\n"
                f"• Estimated timeline: **{total_weeks} weeks** to complete."
            )
        else:
            default_weekly_hours = 10  # 2h/day * 5 days
            est_weeks = math.ceil(total_hours / default_weekly_hours) if total_hours > 0 else 0
            return (
                f"⏱️ **Roadmap Duration Estimate:**\n\n"
                f"• Total curriculum: **{total_hours} study hours** across **{skill_count} skills**.\n"
                f"• At a standard pace of 2 hours/day (5 days/week = 10h/week), this roadmap takes approximately **{est_weeks} weeks** to complete.\n"
                f"*(Configure your daily hours and generate a schedule in the Study Planner tab above for your exact timeline!)*"
            )

    # -------------------------------------------------------------------------
    # Case 4: "schedule" / "routine" / "plan"
    # -------------------------------------------------------------------------
    if any(k in q for k in ["schedule", "routine", "plan", "calendar", "study routine"]):
        if schedule_context:
            weeks_list, total_weeks, h_day, d_week = schedule_context
            preview_lines = []
            for w in weeks_list[:2]:  # Show first 2 weeks
                preview_lines.append(f"**{w['label']}:**")
                for d in w["days"][:3]:  # Show up to 3 days
                    preview_lines.append(f"  • {d['entry']}")
            preview_str = "\n".join(preview_lines)
            return (
                f"📅 **Your Study Routine ({total_weeks} Total Weeks):**\n\n"
                f"{preview_str}\n\n"
                f"*(See the week-by-week table above for your full day-by-day timetable.)*"
            )
        else:
            return (
                "📅 Click the **Generate schedule** button in the Study Planner tab above to calculate your day-by-day timetable!"
            )

    # -------------------------------------------------------------------------
    # Case 5: "what is <skill>" or "resource"
    # -------------------------------------------------------------------------
    if any(k in q for k in ["what is", "what's", "tell me about", "resource for", "resource", "tutorial", "link"]):
        # Find if any known skill is referenced in query
        target_skill = None
        for skill_key in list(SKILL_DESCRIPTIONS.keys()) + [item["skill"].lower() for item in all_roadmap_items]:
            # Use word boundary search
            if re.search(r"\b" + re.escape(skill_key) + r"\b", q):
                target_skill = skill_key
                break

        if target_skill:
            desc = SKILL_DESCRIPTIONS.get(
                target_skill,
                f"Specialized data science and machine learning technology required for {target_skill.title()}."
            )
            res_title, res_url = m4.get_skill_resource(target_skill)
            return (
                f"ℹ️ **{target_skill.title()}**\n\n"
                f"{desc}\n\n"
                f"📖 **Free Resource:** [{res_title}]({res_url})"
            )
        else:
            return (
                "Please specify which skill you'd like to learn about. "
                "For example: *'What is pandas?'* or *'Resource for scikit-learn'*"
            )

    # -------------------------------------------------------------------------
    # Case 6: Anything else -> Polite list of capabilities
    # -------------------------------------------------------------------------
    return (
        "🤖 **Study Assistant Capabilities:**\n\n"
        "I can answer questions based on your personalized roadmap and study plan. Try asking:\n"
        "• *'What should I learn first?'* or *'What is next?'*\n"
        "• *'Why should I learn <skill>?'* (e.g. *'Why numpy?'* or *'Why sql?'*)\n"
        "• *'How long will it take?'* or *'How many weeks?'*\n"
        "• *'What is my study schedule?'* or *'Show routine'*\n"
        "• *'What is <skill>?'* or *'Resource for <skill>?'* (e.g. *'What is scikit-learn?'*)"
    )

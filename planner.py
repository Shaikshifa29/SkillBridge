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
# Comprehensive estimates across Software, Data, AI/ML, Cloud, DevOps, Security
# -----------------------------------------------------------------------------
HOURS = {
    # Core Programming & Web Development
    "python": 15,
    "numpy": 8,
    "pandas": 10,
    "sql": 12,
    "html": 8,
    "css": 8,
    "javascript": 15,
    "typescript": 10,
    "react": 18,
    "next.js": 12,
    "tailwind css": 6,
    "redux": 8,
    "node.js": 15,
    "express": 8,
    "fastapi": 10,
    "django": 15,
    "spring boot": 18,
    "rest apis": 8,
    "graphql": 10,
    "microservices": 15,
    "redis": 8,

    # Classical Machine Learning & Data Science
    "scikit-learn": 20,
    "basic ml": 15,
    "machine learning": 18,
    "classification": 10,
    "regression": 10,
    "clustering": 8,
    "decision trees": 8,
    "data preprocessing": 10,
    "feature engineering": 12,
    "statistics": 12,
    "excel": 8,
    "power bi": 12,
    "tableau": 12,

    # Deep Learning & Modern AI
    "deep learning": 25,
    "pytorch": 20,
    "tensorflow": 20,
    "keras": 10,
    "nlp": 15,
    "neural networks": 15,
    "computer vision": 20,
    "reinforcement learning": 25,
    "generative ai": 15,
    "prompt engineering": 6,
    "llms": 15,
    "langchain": 12,
    "vector databases": 10,
    "mlops": 15,

    # Data Engineering & Warehousing
    "data modeling": 10,
    "data warehousing": 12,
    "dbt": 10,
    "etl pipelines": 12,
    "hadoop": 15,
    "spark": 15,
    "postgresql": 10,
    "mysql": 10,
    "mongodb": 10,

    # Cloud, DevOps & Systems
    "linux": 12,
    "git": 6,
    "docker": 10,
    "kubernetes": 20,
    "aws": 15,
    "azure": 15,
    "gcp": 15,
    "terraform": 12,
    "ci/cd": 10,
    "ansible": 10,
    "prometheus": 8,
    "grafana": 6,
    "sre": 12,
    "bash": 8,

    # Cybersecurity & Networks
    "networking": 15,
    "security fundamentals": 12,
    "cybersecurity": 15,
    "siem tools": 15,
    "wireshark": 8,
    "incident response": 12,
    "penetration testing": 20,
    "ethical hacking": 20,
    "soc analyst": 15,
    "cloud security": 15,
    "cryptography": 12,
    "iam": 8,

    # Mobile & QA Testing
    "react native": 18,
    "flutter": 18,
    "android development": 20,
    "ios development": 20,
    "kotlin": 15,
    "swift": 15,
    "software testing": 10,
    "qa automation": 15,
    "playwright": 10,
    "cypress": 10,
    "api testing": 8,

    # Embedded, Blockchain & Systems
    "c": 18,
    "c++": 25,
    "c#": 18,
    "java": 20,
    "embedded systems": 20,
    "microcontrollers": 15,
    "iot": 15,
    "blockchain": 18,
    "solidity": 15,
    "web3": 12,
    "system administration": 12,
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
# 4. UNIFIED STUDY ASSISTANT (Delegates to ARIS Intelligent Backend)
# Provides intelligent responses via aris_assistant, avoiding conflicting handlers.
# -----------------------------------------------------------------------------
def get_study_assistant_response(query, analysis_results=None, schedule_context=None, chat_history=None, user_profile=None):
    """
    Unified Study Assistant interface delegated directly to ARIS AI Assistant.
    Ensures no conflicting responses, duplicate response boxes, or legacy canned responses.
    """
    import aris_assistant
    return aris_assistant.get_aris_response(
        query=query,
        chat_history=chat_history or [],
        assistant_name="Aris",
        analysis_results=analysis_results,
        schedule_context=schedule_context,
        user_profile=user_profile,
    )


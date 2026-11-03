# database.py - Multi-Tenant Persistent Storage for SkillBridge
# Thread-safe database operations for user profiles, study schedules, and task progress tracking.
# Supports both Supabase PostgREST (cloud) and isolated SQLite (local) keyed by user_id.

import sqlite3
import datetime
import json
import os
from contextlib import closing
from typing import Dict, List, Optional, Tuple, Any
import requests
import supabase_auth

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillbridge.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize multi-tenant database schema ensuring every table has user_id."""
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()

            # Check if legacy study_tasks table exists without user_id column
            cursor.execute("PRAGMA table_info(study_tasks)")
            task_cols = [row[1] for row in cursor.fetchall()]
            if task_cols and "user_id" not in task_cols:
                # Migrate or drop legacy un-scoped study_tasks table
                cursor.execute("DROP TABLE study_tasks")

            # 1. User Profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    email TEXT,
                    target_group TEXT DEFAULT 'Fresher Only',
                    skills_input TEXT DEFAULT '',
                    hours_per_day INTEGER DEFAULT 2,
                    days_per_week INTEGER DEFAULT 5,
                    start_date TEXT,
                    has_analyzed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. User Gap Analysis Results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_gap_analyses (
                    user_id TEXT PRIMARY KEY,
                    skills_input TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    coverage_percentage REAL NOT NULL,
                    matched_count INTEGER NOT NULL,
                    total_top INTEGER NOT NULL,
                    matched_skills TEXT DEFAULT '[]',
                    missing_skills TEXT DEFAULT '[]',
                    not_in_dataset TEXT DEFAULT '[]',
                    main_roadmap TEXT DEFAULT '[]',
                    optional_roadmap TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Study Schedule Metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_schedules (
                    user_id TEXT PRIMARY KEY,
                    total_weeks INTEGER NOT NULL,
                    hours_per_day REAL NOT NULL,
                    days_per_week INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Study Tasks with Completion Tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    week_num INTEGER NOT NULL,
                    week_label TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    day_index INTEGER NOT NULL,
                    task_order INTEGER NOT NULL,
                    skill TEXT NOT NULL,
                    hours REAL NOT NULL,
                    display_text TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, task_id)
                )
            """)

            # 5. Study Assistant Chat History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


# -----------------------------------------------------------------------------
# SUPABASE REST HELPER (Optional cloud sync when credentials provided)
# -----------------------------------------------------------------------------
def _supabase_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    url, anon_key = supabase_auth.get_supabase_config()
    headers = {
        "apikey": anon_key or "",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    if access_token and not access_token.startswith("local_"):
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


# -----------------------------------------------------------------------------
# USER PROFILE PERSISTENCE (Strictly scoped by user_id)
# -----------------------------------------------------------------------------
def get_user_profile(user_id: str, access_token: Optional[str] = None, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Retrieve user-specific profile inputs and preferences."""
    if not user_id:
        return {
            "target_group": "Fresher Only",
            "skills_input": "",
            "hours_per_day": 2,
            "days_per_week": 5,
            "start_date": None,
            "has_analyzed": False,
        }

    init_db(db_path)

    # 1. Try Supabase REST if configured
    url, anon_key = supabase_auth.get_supabase_config()
    if supabase_auth.is_supabase_configured() and access_token and not access_token.startswith("local_"):
        try:
            res = requests.get(
                f"{url}/rest/v1/profiles?id=eq.{user_id}&select=*",
                headers=_supabase_headers(access_token),
                timeout=5
            )
            if res.status_code == 200:
                rows = res.json()
                if rows:
                    p = rows[0]
                    return {
                        "target_group": p.get("target_group") or "Fresher Only",
                        "skills_input": p.get("skills_input") or "",
                        "hours_per_day": int(p.get("hours_per_day") or 2),
                        "days_per_week": int(p.get("days_per_week") or 5),
                        "start_date": p.get("start_date"),
                        "has_analyzed": bool(p.get("has_analyzed", False)),
                    }
        except Exception:
            pass

    # 2. Local SQLite lookup scoped to user_id
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "target_group": row["target_group"] or "Fresher Only",
                "skills_input": row["skills_input"] or "",
                "hours_per_day": int(row["hours_per_day"] or 2),
                "days_per_week": int(row["days_per_week"] or 5),
                "start_date": row["start_date"],
                "has_analyzed": bool(row["has_analyzed"]),
            }

    return {
        "target_group": "Fresher Only",
        "skills_input": "",
        "hours_per_day": 2,
        "days_per_week": 5,
        "start_date": None,
        "has_analyzed": False,
    }


def save_user_profile(
    user_id: str,
    target_group: str,
    skills_input: str,
    has_analyzed: bool = True,
    hours_per_day: int = 2,
    days_per_week: int = 5,
    start_date: Optional[str] = None,
    access_token: Optional[str] = None,
    db_path: str = DB_PATH
) -> None:
    """Save or update user-specific profile in SQLite and Supabase."""
    if not user_id:
        return

    init_db(db_path)
    clean_skills = (skills_input or "").strip()
    analyzed_int = 1 if (has_analyzed and len(clean_skills) > 0) else 0

    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profiles (id, target_group, skills_input, hours_per_day, days_per_week, start_date, has_analyzed, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    target_group = excluded.target_group,
                    skills_input = excluded.skills_input,
                    hours_per_day = excluded.hours_per_day,
                    days_per_week = excluded.days_per_week,
                    start_date = excluded.start_date,
                    has_analyzed = excluded.has_analyzed,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, target_group, clean_skills, hours_per_day, days_per_week, start_date, analyzed_int))

    # Sync to Supabase if configured
    url, anon_key = supabase_auth.get_supabase_config()
    if supabase_auth.is_supabase_configured() and access_token and not access_token.startswith("local_"):
        try:
            headers = _supabase_headers(access_token)
            headers["Prefer"] = "resolution=merge-duplicates"
            payload = {
                "id": user_id,
                "target_group": target_group,
                "skills_input": clean_skills,
                "hours_per_day": hours_per_day,
                "days_per_week": days_per_week,
                "start_date": start_date,
                "has_analyzed": bool(analyzed_int),
                "updated_at": datetime.datetime.now().isoformat(),
            }
            requests.post(f"{url}/rest/v1/profiles", json=payload, headers=headers, timeout=5)
        except Exception:
            pass


# -----------------------------------------------------------------------------
# GAP ANALYSIS PERSISTENCE (Per-user cached analysis)
# -----------------------------------------------------------------------------
def save_gap_analysis(
    user_id: str,
    skills_input: str,
    group_name: str,
    gap_results: Dict[str, Any],
    main_roadmap: List[Dict[str, Any]],
    optional_roadmap: List[Dict[str, Any]],
    access_token: Optional[str] = None,
    db_path: str = DB_PATH
) -> None:
    """Save user-specific gap analysis and roadmap outputs."""
    if not user_id:
        return

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_gap_analyses (
                    user_id, skills_input, group_name, coverage_percentage,
                    matched_count, total_top, matched_skills, missing_skills,
                    not_in_dataset, main_roadmap, optional_roadmap, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    skills_input = excluded.skills_input,
                    group_name = excluded.group_name,
                    coverage_percentage = excluded.coverage_percentage,
                    matched_count = excluded.matched_count,
                    total_top = excluded.total_top,
                    matched_skills = excluded.matched_skills,
                    missing_skills = excluded.missing_skills,
                    not_in_dataset = excluded.not_in_dataset,
                    main_roadmap = excluded.main_roadmap,
                    optional_roadmap = excluded.optional_roadmap,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id,
                skills_input.strip(),
                group_name,
                float(gap_results.get("coverage_percentage", 0.0)),
                int(gap_results.get("matched_count", 0)),
                int(gap_results.get("total_top", 15)),
                json.dumps(gap_results.get("matched_skills", [])),
                json.dumps(gap_results.get("missing_skills", [])),
                json.dumps(gap_results.get("not_in_dataset", [])),
                json.dumps(main_roadmap),
                json.dumps(optional_roadmap),
            ))


def get_saved_gap_analysis(user_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve persisted gap analysis for a specific user."""
    if not user_id:
        return None

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_gap_analyses WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None

        try:
            matched_skills = json.loads(row["matched_skills"])
            missing_skills = json.loads(row["missing_skills"])
            not_in_dataset = json.loads(row["not_in_dataset"])
            main_roadmap = json.loads(row["main_roadmap"])
            optional_roadmap = json.loads(row["optional_roadmap"])
        except Exception:
            return None

        gap_results = {
            "user_skills_clean": [s.strip() for s in row["skills_input"].split(",") if s.strip()],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "not_in_dataset": not_in_dataset,
            "coverage_percentage": float(row["coverage_percentage"]),
            "matched_count": int(row["matched_count"]),
            "total_top": int(row["total_top"]),
            "group_name": row["group_name"],
        }

        return {
            "skills_input": row["skills_input"],
            "group_name": row["group_name"],
            "gap_results": gap_results,
            "main_roadmap": main_roadmap,
            "optional_roadmap": optional_roadmap,
            "unmet_prereqs": [],
        }


def clear_gap_analysis(user_id: str, db_path: str = DB_PATH) -> None:
    """Clear saved gap analysis when inputs are wiped or changed."""
    if not user_id:
        return
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_gap_analyses WHERE user_id = ?", (user_id,))


# -----------------------------------------------------------------------------
# STUDY SCHEDULE & TASK PERSISTENCE (Strictly scoped by user_id)
# -----------------------------------------------------------------------------
def save_study_schedule(
    user_id: str,
    weeks: List[Dict[str, Any]],
    total_weeks: int,
    hours_per_day: float,
    days_per_week: int,
    start_date: Any,
    access_token: Optional[str] = None,
    db_path: str = DB_PATH
) -> None:
    """
    Persist generated study schedule and all individual tasks into SQLite and Supabase.
    Preserves completion status of existing tasks for this user.
    """
    if not user_id:
        return

    init_db(db_path)
    start_date_str = start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date)

    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()

            # Preserve already completed tasks for this user
            cursor.execute(
                "SELECT task_id, skill, hours, date_str FROM study_tasks WHERE user_id = ? AND is_completed = 1",
                (user_id,)
            )
            completed_records = {(row["skill"].lower().strip(), row["date_str"]): True for row in cursor.fetchall()}

            # Save / replace schedule metadata for this user
            cursor.execute("""
                INSERT INTO study_schedules (user_id, total_weeks, hours_per_day, days_per_week, start_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    total_weeks = excluded.total_weeks,
                    hours_per_day = excluded.hours_per_day,
                    days_per_week = excluded.days_per_week,
                    start_date = excluded.start_date,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, int(total_weeks), float(hours_per_day), int(days_per_week), start_date_str))

            # Clear previous tasks for this user only
            cursor.execute("DELETE FROM study_tasks WHERE user_id = ?", (user_id,))

            task_order = 0
            tasks_to_insert = []
            for w in weeks:
                week_num = int(w["week_num"])
                week_label = str(w["label"])
                for day_idx, d in enumerate(w["days"]):
                    date_str = str(d["date_str"])
                    raw_tasks_str = str(d["tasks_str"])

                    day_items = [item.strip() for item in raw_tasks_str.split(",") if item.strip()]
                    for task_idx, item in enumerate(day_items):
                        task_order += 1
                        skill_name = item
                        hours = float(hours_per_day)
                        if "(" in item and item.endswith(")"):
                            parts = item.rsplit("(", 1)
                            skill_name = parts[0].strip()
                            hr_str = parts[1].replace(")", "").replace("h", "").strip()
                            try:
                                hours = float(hr_str)
                            except ValueError:
                                hours = 1.0

                        clean_skill = skill_name.lower().strip()
                        task_id = f"w{week_num}_d{day_idx}_t{task_idx}_{clean_skill}"
                        was_completed = 1 if (clean_skill, date_str) in completed_records else 0

                        cursor.execute("""
                            INSERT INTO study_tasks (
                                user_id, task_id, week_num, week_label, date_str, day_index,
                                task_order, skill, hours, display_text, is_completed
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user_id, task_id, week_num, week_label, date_str, day_idx,
                            task_order, skill_name, hours, item, was_completed
                        ))


def get_saved_study_schedule(user_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieve the persisted study schedule and reconstructed weeks structure for a user.
    Returns None if no schedule has been generated for this user.
    """
    if not user_id:
        return None

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM study_schedules WHERE user_id = ?", (user_id,))
        meta = cursor.fetchone()
        if not meta:
            return None

        # Retrieve tasks ordered by task_order for this user only
        cursor.execute("SELECT * FROM study_tasks WHERE user_id = ? ORDER BY task_order ASC", (user_id,))
        tasks = cursor.fetchall()
        if not tasks:
            return None

        # Reconstruct weeks structure
        weeks_dict: Dict[int, Dict[str, Any]] = {}
        for row in tasks:
            w_num = row["week_num"]
            w_label = row["week_label"]
            d_str = row["date_str"]

            if w_num not in weeks_dict:
                weeks_dict[w_num] = {
                    "week_num": w_num,
                    "label": w_label,
                    "days_dict": {},
                }

            w_entry = weeks_dict[w_num]
            if d_str not in w_entry["days_dict"]:
                w_entry["days_dict"][d_str] = {
                    "date_str": d_str,
                    "tasks": [],
                    "tasks_str_list": []
                }

            w_entry["days_dict"][d_str]["tasks"].append(dict(row))
            w_entry["days_dict"][d_str]["tasks_str_list"].append(row["display_text"])

        reconstructed_weeks = []
        for w_num in sorted(weeks_dict.keys()):
            w_info = weeks_dict[w_num]
            days_list = []
            for d_str, d_info in w_info["days_dict"].items():
                days_list.append({
                    "date_str": d_str,
                    "tasks_str": ", ".join(d_info["tasks_str_list"]),
                    "tasks": d_info["tasks"],
                })
            reconstructed_weeks.append({
                "week_num": w_num,
                "label": w_info["label"],
                "days": days_list,
            })

        start_date_val = meta["start_date"]
        try:
            start_date_obj = datetime.date.fromisoformat(start_date_val)
        except Exception:
            start_date_obj = datetime.date.today()

        return {
            "weeks": reconstructed_weeks,
            "total_weeks": meta["total_weeks"],
            "hours_per_day": meta["hours_per_day"],
            "days_per_week": meta["days_per_week"],
            "start_date": start_date_obj,
        }


def set_task_status(user_id: str, task_id: str, is_completed: bool, db_path: str = DB_PATH) -> None:
    """Mark an individual study task as completed or incomplete for a specific user."""
    if not user_id:
        return

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            status_val = 1 if is_completed else 0
            completed_at_val = datetime.datetime.now().isoformat() if is_completed else None
            cursor.execute("""
                UPDATE study_tasks
                SET is_completed = ?, completed_at = ?
                WHERE user_id = ? AND task_id = ?
            """, (status_val, completed_at_val, user_id, task_id))


def get_all_tasks(user_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all study tasks with completion state for a user."""
    if not user_id:
        return []

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_tasks WHERE user_id = ? ORDER BY task_order ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_learning_progress(user_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Calculate overall learning progress and per-skill completion statistics for a user."""
    if not user_id:
        return {
            "has_schedule": False,
            "total_tasks": 0,
            "completed_tasks": 0,
            "progress_pct": 0.0,
            "total_hours": 0.0,
            "completed_hours": 0.0,
            "skill_progress": {},
        }

    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_tasks WHERE user_id = ?", (user_id,))
        tasks = cursor.fetchall()

        if not tasks:
            return {
                "has_schedule": False,
                "total_tasks": 0,
                "completed_tasks": 0,
                "progress_pct": 0.0,
                "total_hours": 0.0,
                "completed_hours": 0.0,
                "skill_progress": {},
            }

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t["is_completed"])
        total_hours = sum(t["hours"] for t in tasks)
        completed_hours = sum(t["hours"] for t in tasks if t["is_completed"])
        progress_pct = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        skill_stats: Dict[str, Dict[str, Any]] = {}
        for t in tasks:
            skill_key = t["skill"].lower().strip()
            if skill_key not in skill_stats:
                skill_stats[skill_key] = {"total": 0, "completed": 0, "hours": 0.0, "completed_hours": 0.0}
            skill_stats[skill_key]["total"] += 1
            skill_stats[skill_key]["hours"] += t["hours"]
            if t["is_completed"]:
                skill_stats[skill_key]["completed"] += 1
                skill_stats[skill_key]["completed_hours"] += t["hours"]

        skill_progress = {}
        for s_key, s_data in skill_stats.items():
            s_pct = (s_data["completed"] / s_data["total"] * 100.0) if s_data["total"] > 0 else 0.0
            skill_progress[s_key] = {
                "total_tasks": s_data["total"],
                "completed_tasks": s_data["completed"],
                "total_hours": s_data["hours"],
                "completed_hours": s_data["completed_hours"],
                "pct": s_pct,
                "is_complete": s_data["completed"] == s_data["total"] and s_data["total"] > 0,
            }

        return {
            "has_schedule": True,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_pct": progress_pct,
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "skill_progress": skill_progress,
        }


def reset_study_plan(user_id: str, db_path: str = DB_PATH) -> None:
    """Clear study plan and tasks for a specific user."""
    if not user_id:
        return
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM study_tasks WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM study_schedules WHERE user_id = ?", (user_id,))


# -----------------------------------------------------------------------------
# CHAT HISTORY PERSISTENCE (Per-user study assistant conversations)
# -----------------------------------------------------------------------------
def save_chat_message(user_id: str, role: str, content: str, db_path: str = DB_PATH) -> None:
    """Save an exchange into user's chat history."""
    if not user_id:
        return
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )


def get_chat_history(user_id: str, db_path: str = DB_PATH) -> List[Dict[str, str]]:
    """Retrieve chat history for a specific user."""
    if not user_id:
        return []
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]


def clear_chat_history(user_id: str, db_path: str = DB_PATH) -> None:
    """Clear chat history for a specific user."""
    if not user_id:
        return
    init_db(db_path)
    with closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))

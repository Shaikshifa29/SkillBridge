# SkillBridge Streamlit Web Application - Refined Burgundy & Champagne Gold Edition
# User Authentication & Data Isolation with Supabase
# Uses only Streamlit built-in components and maintains strict separation from backend logic.

import streamlit as st
import pandas as pd
import datetime
import importlib

import module2_skill_demand as m2
import module3_gap_analysis as m3
import module4_roadmap as m4
import planner
import database
import supabase_auth

# Explicitly reload backend modules so long-running Streamlit servers
# reload newly defined module-level attributes without process restart.
importlib.reload(m4)
importlib.reload(planner)
importlib.reload(database)
importlib.reload(supabase_auth)

# Initialize multi-tenant persistent database schema
database.init_db()

# Safely extract module-level RESOURCES dictionary
RESOURCES = getattr(m4, "RESOURCES", getattr(m4, "FREE_RESOURCES", {}))

# Configure wide page layout and title using Streamlit built-in config.
st.set_page_config(
    page_title="SkillBridge · Career Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject custom Burgundy & Champagne Gold CSS from style.css.
with open("style.css", "r", encoding="utf-8") as f:
    custom_css = f.read()
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)


# Helper function to format skill display names,
# keeping acronyms ML, SQL, NLP, and R uppercase (e.g. "Basic ML").
def format_skill_name(skill_str: str) -> str:
    """
    Format skill name for UI display.
    Guarantees ML, SQL, NLP, and R remain uppercase (e.g., 'Basic ML').
    Preserves specialized tech capitalization (e.g., 'PyTorch', 'Scikit-Learn', 'PowerBI', 'C++').
    """
    if not skill_str:
        return ""

    clean_str = skill_str.strip()
    clean_lower = clean_str.lower()

    special_cases = {
        "basic ml": "Basic ML",
        "sql": "SQL",
        "nlp": "NLP",
        "r": "R",
        "scikit-learn": "Scikit-Learn",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "powerbi": "PowerBI",
        "c++": "C++",
        "aws": "AWS",
        "gcp": "GCP",
        "ci/cd": "CI/CD",
        "nosql": "NoSQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",
        "opencv": "OpenCV",
        "nltk": "NLTK",
        "onnx": "ONNX",
        "llms": "LLMs",
        "mlops": "MLOps",
        "advanced ml/dl": "Advanced ML/DL",
        "ml/dl": "ML/DL",
        "ml basics": "ML Basics",
        "ml frameworks": "ML Frameworks",
        "ml fundamentals": "ML Fundamentals",
        "ml libraries": "ML Libraries",
        "basic ml algorithms": "Basic ML Algorithms",
        "basic ml models": "Basic ML Models",
    }
    if clean_lower in special_cases:
        return special_cases[clean_lower]

    words = clean_lower.split()
    formatted_words = []
    for word in words:
        if word in ("ml", "sql", "nlp", "r", "ai", "dl"):
            formatted_words.append(word.upper())
        elif "/" in word:
            parts = [p.upper() if p in ("ml", "sql", "nlp", "r", "ai", "dl", "ci", "cd") else p.capitalize() for p in word.split("/")]
            formatted_words.append("/".join(parts))
        elif "-" in word:
            parts = [p.upper() if p in ("ml", "sql", "nlp", "r", "ai", "dl") else p.capitalize() for p in word.split("-")]
            formatted_words.append("-".join(parts))
        else:
            formatted_words.append(word.capitalize())

    return " ".join(formatted_words)


# Helper for consistent, refined empty states across tabs
def render_empty_state(feature_name: str):
    """Render an elegant human-designed empty state placeholder."""
    st.markdown(
        f"""
        <div class="empty-state-card">
            <div class="empty-state-icon">✦</div>
            <h3>Awaiting Profile Analysis</h3>
            <p>Select your target career group and enter your technical skillset in the sidebar, then click <strong>Analyze</strong> to unlock your {feature_name}.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Callback for updating individual task completion in persistent database
def handle_task_toggle(task_id: str):
    """Save updated task completion state scoped to current authenticated user."""
    auth_user = st.session_state.get("authenticated_user")
    if not auth_user:
        return
    u_id = auth_user["id"]
    checkbox_val = st.session_state.get(f"task_chk_{task_id}", False)
    database.set_task_status(u_id, task_id, checkbox_val)


# =============================================================================
# AUTHENTICATION GATE (Supabase Auth / Data Isolation)
# =============================================================================
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

# Hero section (always visible)
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">Career Intelligence & Strategic Skill Mapping</div>
    <h1 class="hero-title">SkillBridge</h1>
    <p class="hero-subtitle">Bridge the gap between your technical background and real-world market demand in AI, Machine Learning, and Data Science. Identify missing proficiencies and generate a structured learning path.</p>
</div>
""", unsafe_allow_html=True)

# If NOT logged in, show the Authentication portal
if st.session_state["authenticated_user"] is None:
    is_cloud = supabase_auth.is_supabase_configured()

    _, auth_center_col, _ = st.columns([1, 2, 1])

    with auth_center_col:
        st.markdown("""
        <div class="auth-header-card">
            <div class="auth-header-title">Member Workspace</div>
            <div class="auth-header-caption">Sign in or create an account to access your personal career intelligence workspace and persistent study plan.</div>
        </div>
        """, unsafe_allow_html=True)

        if is_cloud:
            st.markdown(
                '<div style="text-align: center; margin-top: 8px;"><span class="auth-config-pill">⚡ Supabase Cloud Auth Active</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="text-align: center; margin-top: 8px;"><span class="auth-config-pill">🔒 Secure Local Auth Mode (Configure Supabase in .streamlit/secrets.toml for Cloud Sync)</span></div>',
                unsafe_allow_html=True
            )

        auth_tab_signin, auth_tab_signup, auth_tab_forgot = st.tabs([
            "Sign In", "Create Account", "Forgot Password"
        ])

        # TAB: Sign In
        with auth_tab_signin:
            with st.form("signin_form", clear_on_submit=False):
                st.write("")
                signin_email = st.text_input("Email Address", placeholder="name@domain.com")
                signin_password = st.text_input("Password", type="password", placeholder="Enter your password")
                signin_submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if signin_submit:
                    success, msg, user_obj = supabase_auth.sign_in(signin_email, signin_password)
                    if success and user_obj:
                        st.session_state["authenticated_user"] = user_obj
                        st.session_state["_active_user_id"] = user_obj["id"]
                        st.success("Signed in successfully! Loading your workspace...")
                        st.rerun()
                    else:
                        st.error(msg)

        # TAB: Create Account
        with auth_tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                st.write("")
                signup_email = st.text_input("Email Address", placeholder="name@domain.com")
                signup_password = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters")
                signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")
                signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if signup_submit:
                    if signup_password != signup_confirm:
                        st.error("Passwords do not match. Please try again.")
                    else:
                        success, msg, user_obj = supabase_auth.sign_up(signup_email, signup_password)
                        if success:
                            if user_obj and not user_obj.get("pending_verification"):
                                st.session_state["authenticated_user"] = user_obj
                                st.session_state["_active_user_id"] = user_obj["id"]
                                st.success("Account created and signed in! Welcome to SkillBridge.")
                                st.rerun()
                            else:
                                st.info(msg)
                        else:
                            st.error(msg)

        # TAB: Forgot Password
        with auth_tab_forgot:
            with st.form("forgot_password_form", clear_on_submit=False):
                st.write("")
                forgot_email = st.text_input("Your Registered Email", placeholder="name@domain.com")
                forgot_submit = st.form_submit_button("Send Reset Instructions", type="secondary", use_container_width=True)

                if forgot_submit:
                    success, msg = supabase_auth.reset_password_for_email(forgot_email)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    # Stop rendering remainder of app until user signs in
    st.markdown("---")
    st.caption("SkillBridge · Multi-User Career Intelligence · Real-time Skill Gap Analysis & Learning Journey")
    st.stop()


# =============================================================================
# AUTHENTICATED WORKSPACE (User Session & Isolated Data Scoping)
# =============================================================================
current_user = st.session_state["authenticated_user"]
user_id = str(current_user["id"])
user_email = current_user.get("email", "Member")
access_token = current_user.get("access_token")

# When switching users or on fresh login, reset user-specific session state
if st.session_state.get("_active_user_id") != user_id:
    st.session_state["_active_user_id"] = user_id
    st.session_state["analysis_results"] = None
    st.session_state["schedule_results"] = None
    st.session_state["chat_messages"] = None
    st.session_state["confirm_reset_plan"] = False

# Sidebar: Authenticated User Information & Sign Out Button
st.sidebar.markdown(f"""
<div class="user-session-card">
    <div class="user-badge">Signed In</div>
    <div class="user-email">{user_email}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Sign Out", type="secondary", use_container_width=True):
    supabase_auth.sign_out(access_token)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.divider()

# Load user-specific profile from database (scoped to user_id)
user_profile = database.get_user_profile(user_id, access_token)
saved_target_group = user_profile.get("target_group", "Fresher Only")
saved_skills_input = (user_profile.get("skills_input") or "").strip()
group_index = 0 if saved_target_group == "All Roles" else 1

# Sidebar: Profile Settings
st.sidebar.markdown("### Profile Settings")
st.sidebar.caption("Benchmark your skillset against verified job market postings.")

group_selector = st.sidebar.selectbox(
    "Target Career Group",
    options=["All Roles", "Fresher Only"],
    index=group_index,
    help="Select whether to compare against all roles or entry-level/fresher postings."
)

skills_input = st.sidebar.text_area(
    "Current Technical Skills:",
    value=saved_skills_input,
    height=130,
    placeholder="e.g. Python, SQL, Pandas, Scikit-Learn",
    help="Type your current technical skills separated by commas."
)

analyze_button = st.sidebar.button("Analyze", type="primary")

group_code = "1" if group_selector == "All Roles" else "2"
clean_skills = skills_input.strip() if skills_input else ""
is_skills_empty = len(clean_skills) == 0

# Stale analysis invalidation:
# If user cleared the input, immediately invalidate previous results
if is_skills_empty:
    if st.session_state.get("analysis_results") is not None:
        st.session_state["analysis_results"] = None
    database.clear_gap_analysis(user_id)
    database.save_user_profile(user_id, group_selector, "", has_analyzed=False, access_token=access_token)
else:
    # If the user changed the skills or group in the UI without clicking Analyze,
    # invalidate old stale analysis so we do not display mismatched results!
    curr_res = st.session_state.get("analysis_results")
    if curr_res is not None:
        res_skills = curr_res.get("skills_input", "").strip()
        res_group = curr_res.get("group_name", "")
        if res_skills != clean_skills or res_group != group_selector:
            st.session_state["analysis_results"] = None
            st.sidebar.info("💡 Skills or career group modified. Click **Analyze** to generate your updated Gap Analysis.")

# Analyze button trigger
if analyze_button:
    if is_skills_empty:
        st.sidebar.warning("⚠️ Please enter at least one technical skill before analyzing.")
        st.session_state["analysis_results"] = None
        database.clear_gap_analysis(user_id)
        database.save_user_profile(user_id, group_selector, "", has_analyzed=False, access_token=access_token)
    else:
        # Run Module 3 gap analysis
        gap_results = m3.run_module_3(
            user_skills_input=clean_skills,
            group_choice=group_code
        )

        # Run Module 4 roadmap generator
        main_roadmap, optional_roadmap, unmet_prereqs = m4.generate_roadmap_from_gap(gap_results)

        roadmap_fallback_skills = [
            item["skill"] for item in (main_roadmap + optional_roadmap)
            if item["skill"].lower().strip() not in RESOURCES
        ]

        # Save to database scoped to this user
        database.save_user_profile(
            user_id,
            target_group=group_selector,
            skills_input=clean_skills,
            has_analyzed=True,
            access_token=access_token
        )
        database.save_gap_analysis(
            user_id,
            skills_input=clean_skills,
            group_name=group_selector,
            gap_results=gap_results,
            main_roadmap=main_roadmap,
            optional_roadmap=optional_roadmap,
            access_token=access_token
        )

        st.session_state["analysis_results"] = {
            "skills_input": clean_skills,
            "group_name": group_selector,
            "gap_results": gap_results,
            "main_roadmap": main_roadmap,
            "optional_roadmap": optional_roadmap,
            "unmet_prereqs": unmet_prereqs,
            "fallback_skills": roadmap_fallback_skills,
        }

# Auto-restore analysis results from database if not in session state
if not is_skills_empty and st.session_state.get("analysis_results") is None:
    saved_analysis = database.get_saved_gap_analysis(user_id)
    if (
        saved_analysis is not None
        and saved_analysis.get("skills_input", "").strip() == clean_skills
        and saved_analysis.get("group_name") == group_selector
    ):
        st.session_state["analysis_results"] = saved_analysis

# Auto-restore saved study schedule from database if not in session state
if st.session_state.get("schedule_results") is None:
    persisted_schedule = database.get_saved_study_schedule(user_id)
    if persisted_schedule is not None:
        st.session_state["schedule_results"] = persisted_schedule

# Auto-restore chat messages from database if not initialized
if st.session_state.get("chat_messages") is None:
    st.session_state["chat_messages"] = database.get_chat_history(user_id)

# Retrieve active analysis results
results_data = st.session_state.get("analysis_results")
if results_data is not None:
    gap_results = results_data["gap_results"]
    main_roadmap = results_data["main_roadmap"]
    optional_roadmap = results_data["optional_roadmap"]
    selected_group = results_data["group_name"]
else:
    gap_results = None
    main_roadmap = []
    optional_roadmap = []
    selected_group = None

# Query persistent learning progress across tasks for this user
learning_progress = database.get_learning_progress(user_id)

# Define the four navigation tabs
tab_gap, tab_roadmap, tab_demand, tab_planner = st.tabs([
    "Gap Analysis", "Roadmap", "Market Demand", "Study Planner"
])

# =========================================================================
# TAB 1: GAP ANALYSIS
# =========================================================================
with tab_gap:
    if is_skills_empty:
        st.markdown("""
        <div class="empty-state-card">
            <div class="empty-state-icon">✦</div>
            <h3>Technical Skills Required</h3>
            <p>Please enter your current technical skills (e.g. <em>Python, SQL, Pandas</em>) in the sidebar and click <strong>Analyze</strong> to perform your skill gap analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    elif results_data is not None:
        st.subheader("Skill Gap & Market Alignment Overview")
        st.caption("Quantified evaluation of your current competencies versus market demand.")

        coverage_score = gap_results["coverage_percentage"]
        matched_count = gap_results["matched_count"]
        total_top = gap_results["total_top"]
        missing_count = len(gap_results["missing_skills"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric(
                label="Coverage Score",
                value=f"{coverage_score:.1f}%"
            )
        with col_metric2:
            st.metric(
                label="Skills Known",
                value=f"{matched_count} / {total_top}"
            )
        with col_metric3:
            st.metric(
                label="Skills Missing",
                value=f"{missing_count}"
            )

        progress_val = min(1.0, max(0.0, coverage_score / 100.0))
        st.progress(progress_val, text=f"Top 15 Market Alignment: {coverage_score:.1f}%")

        st.divider()

        col_have, col_missing = st.columns(2)

        with col_have:
            st.markdown("#### Matched Skills (Top 15 Alignment)")
            if gap_results["matched_skills"]:
                have_df = pd.DataFrame([
                    {
                        "Rank": f"#{rank}",
                        "Skill": format_skill_name(skill),
                        "Market Demand": f"{pct:.1f}%"
                    }
                    for rank, skill, pct in gap_results["matched_skills"]
                ])
                st.dataframe(have_df, width="stretch", hide_index=True)
            else:
                st.info("None of your entered skills match the top 15 skills for this group.")

        with col_missing:
            st.markdown("#### Missing High-Demand Skills")
            if gap_results["missing_skills"]:
                missing_df = pd.DataFrame([
                    {
                        "Rank": f"#{rank}",
                        "Missing Skill": format_skill_name(skill),
                        "Market Demand": f"{pct:.1f}%"
                    }
                    for rank, skill, pct in gap_results["missing_skills"]
                ])
                st.dataframe(missing_df, width="stretch", hide_index=True)
            else:
                st.success("Incredible! You have mastered all top 15 skills.")

        st.divider()
        st.markdown("#### Typed Skills Not Found in Dataset")
        if gap_results["not_in_dataset"]:
            st.caption("The following skills were not found in any job postings in this dataset:")
            cols_unknown = st.columns(min(4, len(gap_results["not_in_dataset"])))
            for idx, skill in enumerate(gap_results["not_in_dataset"]):
                with cols_unknown[idx % len(cols_unknown)]:
                    st.info(f"🔍 **{format_skill_name(skill)}**")
        else:
            st.caption("All typed skills were recognized in the dataset.")
    else:
        render_empty_state("Gap Analysis dashboard")

# =========================================================================
# TAB 2: ROADMAP
# =========================================================================
with tab_roadmap:
    if is_skills_empty:
        st.markdown("""
        <div class="empty-state-card">
            <div class="empty-state-icon">✦</div>
            <h3>Technical Skills Required</h3>
            <p>Please enter your technical skills in the sidebar and click <strong>Analyze</strong> to generate your personalized learning journey.</p>
        </div>
        """, unsafe_allow_html=True)
    elif results_data is not None:
        st.subheader("Personalized Learning Journey")
        st.caption("Structured progression: Foundational prerequisites precede advanced core skills, ordered by market demand.")

        core_count = len(main_roadmap)
        unmet_count = sum(1 for item in main_roadmap if item["is_unmet_prereq"])
        elective_count = len(optional_roadmap)

        st.markdown(f"""
        <div class="chart-highlight-strip">
            <div class="chart-highlight-pill">Total Curriculum Milestones: <strong>{core_count + elective_count} Skills</strong></div>
            <div class="chart-highlight-pill">Prerequisite Dependencies: <strong>{unmet_count} Identified</strong></div>
            <div class="chart-highlight-pill">Elective Technologies: <strong>{elective_count} Tracks</strong></div>
        </div>
        """, unsafe_allow_html=True)

        if learning_progress["has_schedule"]:
            st.markdown(f"#### 🏆 Learning Journey Progress: {learning_progress['progress_pct']:.1f}% Mastered")
            st.progress(
                learning_progress["progress_pct"] / 100.0,
                text=f"{learning_progress['completed_tasks']} of {learning_progress['total_tasks']} tasks completed ({learning_progress['completed_hours']:.1f} / {learning_progress['total_hours']:.1f} hrs)"
            )
            st.write("")

        st.markdown("#### Core AI / ML & Data Science Track")
        if main_roadmap:
            for idx, item in enumerate(main_roadmap, start=1):
                clean_skill_key = item["skill"].lower().strip()
                skill_stat = learning_progress["skill_progress"].get(clean_skill_key)

                with st.container(border=True):
                    status_class = "status-prerequisite" if item["is_unmet_prereq"] else "status-core"
                    st.markdown(f'<span class="{status_class}"></span>', unsafe_allow_html=True)

                    col_info, col_action = st.columns([3, 1])

                    with col_info:
                        formatted_skill = format_skill_name(item["skill"])
                        st.markdown(f"**Step {idx:02d}: {formatted_skill}**")

                        res_title, res_url = m4.get_skill_resource(clean_skill_key)
                        if clean_skill_key not in RESOURCES:
                            res_title = f"{formatted_skill} Tutorial for Beginners (Google Search)"

                        st.caption(f"📖 {res_title}")

                    with col_action:
                        if item["is_unmet_prereq"]:
                            st.markdown(f":orange-background[**Prerequisite**] · **{item['demand_pct']:.1f}%**")
                        else:
                            st.markdown(f":blue-background[**Core**] · **{item['demand_pct']:.1f}%**")

                        if skill_stat:
                            if skill_stat["is_complete"]:
                                st.markdown(":green-background[**✓ Mastered**]")
                            elif skill_stat["completed_tasks"] > 0:
                                st.markdown(f":violet-background[**In Progress ({skill_stat['pct']:.0f}%)**]")

                        st.link_button("Open resource ↗", res_url)
        else:
            st.success("Your core roadmap is complete! All required core skills are mastered.")

        if optional_roadmap:
            st.divider()
            st.markdown("#### Optional & Specialized Electives (Alternative Languages & Big Data)")
            st.caption("Specialized technologies ordered by market demand percentage.")

            for idx, item in enumerate(optional_roadmap, start=1):
                clean_skill_key = item["skill"].lower().strip()
                skill_stat = learning_progress["skill_progress"].get(clean_skill_key)

                with st.container(border=True):
                    st.markdown('<span class="status-optional"></span>', unsafe_allow_html=True)

                    col_info, col_action = st.columns([3, 1])

                    with col_info:
                        formatted_skill = format_skill_name(item["skill"])
                        st.markdown(f"**Elective: {formatted_skill}**")

                        res_title, res_url = m4.get_skill_resource(clean_skill_key)
                        if clean_skill_key not in RESOURCES:
                            res_title = f"{formatted_skill} Tutorial for Beginners (Google Search)"

                        st.caption(f"📖 {res_title}")

                    with col_action:
                        st.markdown(f":green-background[**Optional**] · **{item['demand_pct']:.1f}%**")

                        if skill_stat:
                            if skill_stat["is_complete"]:
                                st.markdown(":green-background[**✓ Mastered**]")
                            elif skill_stat["completed_tasks"] > 0:
                                st.markdown(f":violet-background[**In Progress ({skill_stat['pct']:.0f}%)**]")

                        st.link_button("Open resource ↗", res_url)
    else:
        render_empty_state("Personalized Learning Journey")

# =========================================================================
# TAB 3: MARKET DEMAND
# =========================================================================
with tab_demand:
    if results_data is not None:
        st.subheader(f"Top 15 Demanded Skills — {selected_group}")
        st.caption(f"Demand percentage calculated across real-world job postings in the {selected_group} cohort.")

        top_15_skills = gap_results["group_demand"][:15]

        top_skill_name = format_skill_name(top_15_skills[0][0])
        top_skill_pct = top_15_skills[0][2]
        avg_top15_pct = sum(item[2] for item in top_15_skills) / len(top_15_skills)

        st.markdown(f"""
        <div class="chart-highlight-strip">
            <div class="chart-highlight-pill">Highest Market Demand: <strong>{top_skill_name} ({top_skill_pct:.1f}%)</strong></div>
            <div class="chart-highlight-pill">Top 15 Benchmark Average: <strong>{avg_top15_pct:.1f}%</strong></div>
            <div class="chart-highlight-pill">Selected Group: <strong>{selected_group}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        chart_df = pd.DataFrame({
            "Skill": [format_skill_name(item[0]) for item in top_15_skills],
            "Demand (%)": [item[2] for item in top_15_skills]
        }).set_index("Skill")

        st.bar_chart(chart_df, color="#D6B875", height=420)

        st.markdown("#### Demand Breakdown Table")
        demand_table_df = pd.DataFrame([
            {
                "Rank": f"#{idx + 1}",
                "Skill Name": format_skill_name(item[0]),
                "Postings Count": item[1],
                "Market Demand": f"{item[2]:.1f}%"
            }
            for idx, item in enumerate(top_15_skills)
        ])
        st.dataframe(demand_table_df, width="stretch", hide_index=True)
    else:
        render_empty_state("Market Demand analysis")

# =========================================================================
# TAB 4: STUDY PLANNER & RULE-BASED ASSISTANT
# =========================================================================
with tab_planner:
    st.subheader("Study Planner & Assistant")
    st.caption("Customize your weekly study schedule, track individual tasks, and chat with your study assistant.")

    saved_hpd = int(user_profile.get("hours_per_day", 2))
    saved_dpw = int(user_profile.get("days_per_week", 5))
    saved_start_str = user_profile.get("start_date")
    try:
        saved_start_val = datetime.date.fromisoformat(saved_start_str) if saved_start_str else datetime.date.today()
    except Exception:
        saved_start_val = datetime.date.today()

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        hours_per_day = st.number_input(
            "Hours per day (1 - 6):",
            min_value=1,
            max_value=6,
            value=saved_hpd,
            step=1,
            help="Daily study time commitment in hours."
        )
    with col_p2:
        days_per_week = st.number_input(
            "Study days per week (3 - 7):",
            min_value=3,
            max_value=7,
            value=saved_dpw,
            step=1,
            help="Number of active study days per week."
        )
    with col_p3:
        start_date = st.date_input(
            "Start date:",
            value=saved_start_val,
            help="Starting date for your learning schedule."
        )

    btn_col, _ = st.columns([2, 5])
    with btn_col:
        gen_schedule_btn = st.button("Generate schedule", type="primary")

    if gen_schedule_btn:
        if is_skills_empty or results_data is None:
            st.warning("⚠️ Please enter your skills and click **Analyze** in the sidebar first to build your roadmap before generating a schedule.")
        else:
            combined_roadmap = main_roadmap + optional_roadmap
            weeks, total_weeks = planner.make_schedule(
                combined_roadmap, hours_per_day, days_per_week, start_date
            )
            # Persist to database scoped to user_id
            database.save_study_schedule(
                user_id=user_id,
                weeks=weeks,
                total_weeks=total_weeks,
                hours_per_day=hours_per_day,
                days_per_week=days_per_week,
                start_date=start_date,
                access_token=access_token
            )
            database.save_user_profile(
                user_id=user_id,
                target_group=group_selector,
                skills_input=clean_skills,
                has_analyzed=True,
                hours_per_day=hours_per_day,
                days_per_week=days_per_week,
                start_date=start_date.isoformat(),
                access_token=access_token
            )

            # Load freshly persisted schedule for this user
            st.session_state["schedule_results"] = database.get_saved_study_schedule(user_id)
            st.rerun()

    # Study Planner Schedule View
    if st.session_state.get("schedule_results") is not None:
        sched = st.session_state["schedule_results"]
        weekly_hours = int(sched["hours_per_day"] * sched["days_per_week"])
        est_end_date = sched["start_date"] + datetime.timedelta(weeks=sched["total_weeks"])

        st.markdown("#### 📅 Active Learning Schedule & Progress")

        # Refresh learning progress
        progress_info = database.get_learning_progress(user_id)
        comp_tasks = progress_info["completed_tasks"]
        tot_tasks = progress_info["total_tasks"]
        comp_pct = progress_info["progress_pct"]
        comp_hrs = progress_info["completed_hours"]
        tot_hrs = progress_info["total_hours"]

        col_pr1, col_pr2, col_pr3, col_pr4 = st.columns(4)
        with col_pr1:
            st.metric("Tasks Completed", f"{comp_tasks} / {tot_tasks}")
        with col_pr2:
            st.metric("Study Progress", f"{comp_pct:.1f}%")
        with col_pr3:
            st.metric("Hours Finished", f"{comp_hrs:.1f} / {tot_hrs:.1f}h")
        with col_pr4:
            st.metric("Hours Remaining", f"{max(0.0, tot_hrs - comp_hrs):.1f}h")

        st.progress(
            comp_pct / 100.0,
            text=f"Total Curriculum Completion: {comp_pct:.1f}% ({comp_tasks} of {tot_tasks} tasks)"
        )

        st.markdown(f"""
        <div class="schedule-summary-strip">
            <div class="schedule-summary-card">
                <div class="label">Total Duration</div>
                <div class="value">{sched['total_weeks']} Weeks</div>
            </div>
            <div class="schedule-summary-card">
                <div class="label">Weekly Commitment</div>
                <div class="value">{weekly_hours} Hours/Wk</div>
            </div>
            <div class="schedule-summary-card">
                <div class="label">Pace & Routine</div>
                <div class="value">{sched['hours_per_day']}h / {sched['days_per_week']} days</div>
            </div>
            <div class="schedule-summary-card">
                <div class="label">Estimated Completion</div>
                <div class="value">{est_end_date.strftime('%d %b %Y')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        view_mode = st.radio(
            "Schedule Display Mode:",
            options=["Interactive Checklist", "Table Overview"],
            horizontal=True,
            help="Check off daily study tasks or view the full schedule as a table."
        )

        if view_mode == "Interactive Checklist":
            st.caption("Check tasks as you complete them. Progress is saved permanently to your account and syncs with the Roadmap.")

            for w in sched["weeks"]:
                w_num = w["week_num"]
                w_label = w["label"]
                w_tasks = [t for d in w["days"] for t in d.get("tasks", [])]
                w_done = sum(1 for t in w_tasks if t.get("is_completed"))
                w_total = len(w_tasks)
                w_badge = f"— {w_done}/{w_total} completed" if w_total > 0 else ""

                with st.expander(f"**{w_label}** {w_badge}", expanded=(w_num == 1 or w_done < w_total)):
                    for d in w["days"]:
                        st.markdown(f"**{d['date_str']}**")
                        day_tasks = d.get("tasks", [])
                        if day_tasks:
                            for task in day_tasks:
                                tid = task["task_id"]
                                is_done = bool(task.get("is_completed", 0))
                                st.checkbox(
                                    label=f"{task['display_text']}",
                                    value=is_done,
                                    key=f"task_chk_{tid}",
                                    on_change=handle_task_toggle,
                                    args=(tid,)
                                )
                        else:
                            st.caption(d.get("tasks_str", "Rest day"))
        else:
            table_rows = []
            for w in sched["weeks"]:
                week_num_label = w["label"]
                for d in w["days"]:
                    day_tasks = d.get("tasks", [])
                    status_text = "✓ Completed" if (day_tasks and all(t.get("is_completed") for t in day_tasks)) else "Pending"
                    table_rows.append({
                        "Status": status_text,
                        "Week": week_num_label,
                        "Day / Date": d["date_str"],
                        "Scheduled Tasks": d["tasks_str"]
                    })
            if table_rows:
                schedule_df = pd.DataFrame(table_rows)
                st.dataframe(schedule_df, width="stretch", hide_index=True)

        # Clear/Reset study plan with 2-step confirmation
        st.markdown("---")
        col_reset_btn, _ = st.columns([3, 5])
        with col_reset_btn:
            if not st.session_state.get("confirm_reset_plan", False):
                if st.button("Reset Study Plan", type="secondary", help="Clear study schedule and all progress"):
                    st.session_state["confirm_reset_plan"] = True
                    st.rerun()

        if st.session_state.get("confirm_reset_plan", False):
            with st.container(border=True):
                st.warning("⚠️ **Confirmation Required**: Are you sure you want to reset your study schedule and clear all task progress? This action cannot be undone.")
                col_c1, col_c2, _ = st.columns([2, 2, 6])
                with col_c1:
                    if st.button("Yes, Reset Everything", type="primary"):
                        database.reset_study_plan(user_id)
                        st.session_state["schedule_results"] = None
                        st.session_state["confirm_reset_plan"] = False
                        st.success("Study plan and all task progress have been reset.")
                        st.rerun()
                with col_c2:
                    if st.button("Cancel"):
                        st.session_state["confirm_reset_plan"] = False
                        st.rerun()
    else:
        st.markdown("""
        <div class="empty-state-card">
            <div class="empty-state-icon">📅</div>
            <h3>No Active Study Plan</h3>
            <p>Enter your technical skills in the sidebar, click <strong>Analyze</strong>, set your daily hours and study days above, then click <strong>Generate schedule</strong> to create your personalized plan.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Chat Area using st.chat_input and st.chat_message
    st.markdown("#### 💬 Study Assistant Chat")
    st.caption("Ask questions about your study roadmap, prerequisites, duration, routine, or resources.")

    # Render existing conversation messages for this user
    for msg in (st.session_state.get("chat_messages") or []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_query = st.chat_input("Ask study assistant (e.g. 'What first?', 'Why numpy?', 'How long?', 'What is scikit-learn?')")
    if user_query:
        if st.session_state["chat_messages"] is None:
            st.session_state["chat_messages"] = []

        # Record user query
        st.session_state["chat_messages"].append({"role": "user", "content": user_query})
        database.save_chat_message(user_id, "user", user_query)

        with st.chat_message("user"):
            st.markdown(user_query)

        sched_context = None
        if st.session_state.get("schedule_results") is not None:
            sr = st.session_state["schedule_results"]
            sched_context = (sr["weeks"], sr["total_weeks"], sr["hours_per_day"], sr["days_per_week"])

        reply = planner.get_study_assistant_response(
            query=user_query,
            analysis_results=st.session_state.get("analysis_results"),
            schedule_context=sched_context
        )

        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        database.save_chat_message(user_id, "assistant", reply)

        with st.chat_message("assistant"):
            st.markdown(reply)

    st.markdown("---")
    st.caption("Rule-based assistant. Time estimates are approximate.")

# Footer
st.markdown("---")
st.caption("Prototype on a public job-description dataset; results are indicative.")

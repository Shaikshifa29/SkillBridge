# SkillBridge Streamlit Web Application - Refined Burgundy & Champagne Gold Edition
# User Authentication & Data Isolation with Supabase
# Uses only Streamlit built-in components and maintains strict separation from backend logic.

import streamlit as st
import pandas as pd
import datetime
import importlib
import os

import module2_skill_demand as m2
import module3_gap_analysis as m3
import module4_roadmap as m4
import planner
import database
import supabase_auth
import aris_assistant
import career_roles

# Explicitly reload backend modules so long-running Streamlit servers
# reload newly defined module-level attributes without process restart.
importlib.reload(m4)
importlib.reload(planner)
importlib.reload(database)
importlib.reload(supabase_auth)
importlib.reload(aris_assistant)
importlib.reload(career_roles)


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

# Restore authenticated session across page reloads / reopen
if st.session_state["authenticated_user"] is None:
    session_token = st.query_params.get("session")
    if session_token:
        restored = database.get_user_session(session_token)
        if restored:
            st.session_state["authenticated_user"] = restored
            st.session_state["_active_user_id"] = restored["id"]

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
                        st.session_state["_last_signin_email"] = None
                        st.session_state["_signin_unconfirmed"] = False

                        # Persist session token for page refreshes
                        token = database.create_user_session(user_obj)
                        st.query_params["session"] = token

                        st.success("Signed in successfully! Loading your workspace...")
                        st.rerun()
                    else:
                        st.error(msg)
                        if user_obj and user_obj.get("pending_verification"):
                            st.session_state["_signin_unconfirmed"] = True
                            st.session_state["_last_signin_email"] = supabase_auth.sanitize_email(signin_email)

            # Actionable Resend Confirmation Button if email is unconfirmed
            if st.session_state.get("_signin_unconfirmed") and st.session_state.get("_last_signin_email"):
                st.info(f"Need another verification link for **{st.session_state['_last_signin_email']}**?")
                if st.button("Resend Confirmation Email", key="btn_resend_confirm"):
                    ok_resend, resend_msg = supabase_auth.resend_confirmation(st.session_state["_last_signin_email"])
                    if ok_resend:
                        st.success(resend_msg)
                        st.session_state["_signin_unconfirmed"] = False
                    else:
                        st.error(resend_msg)

        # TAB: Create Account
        with auth_tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                st.write("")
                signup_full_name = st.text_input("Full Name", placeholder="e.g. Alex Johnson")
                signup_email = st.text_input("Email Address", placeholder="name@domain.com")
                signup_password = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters")
                signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")
                signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if signup_submit:
                    clean_full_name = (signup_full_name or "").strip()
                    clean_signup_email = supabase_auth.sanitize_email(signup_email)
                    if not clean_full_name:
                        st.error("Please enter your full name.")
                    elif not clean_signup_email or not supabase_auth.is_valid_email_format(clean_signup_email):
                        st.error("Please enter a valid email address (e.g. name@domain.com).")
                    elif len(signup_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif signup_password != signup_confirm:
                        st.error("Passwords do not match. Please try again.")
                    else:
                        success, msg, user_obj = supabase_auth.sign_up(
                            clean_signup_email,
                            signup_password,
                            full_name=clean_full_name
                        )
                        if success:
                            if user_obj and not user_obj.get("pending_verification"):
                                st.session_state["authenticated_user"] = user_obj
                                st.session_state["_active_user_id"] = user_obj["id"]

                                # Save user profile with full_name
                                database.save_user_profile(
                                    user_obj["id"],
                                    full_name=clean_full_name,
                                    target_group=career_roles.DEFAULT_ROLE,
                                    skills_input="",
                                    has_analyzed=False,
                                    access_token=user_obj.get("access_token")
                                )

                                # Persist session token for page refreshes
                                token = database.create_user_session(user_obj)
                                st.query_params["session"] = token

                                st.success("Account created and signed in! Welcome to SkillBridge.")
                                st.rerun()
                            else:
                                st.info(msg)
                                st.session_state["_last_signin_email"] = clean_signup_email
                        else:
                            st.error(msg)

        # TAB: Forgot Password
        with auth_tab_forgot:
            with st.form("forgot_password_form", clear_on_submit=False):
                st.write("")
                forgot_email = st.text_input("Your Registered Email", placeholder="name@domain.com")
                forgot_submit = st.form_submit_button("Send Reset Instructions", type="secondary", use_container_width=True)

                if forgot_submit:
                    clean_forgot_email = supabase_auth.sanitize_email(forgot_email)
                    if not supabase_auth.is_valid_email_format(clean_forgot_email):
                        st.error("Please enter a valid email address (e.g. name@domain.com).")
                    else:
                        success, msg = supabase_auth.reset_password_for_email(clean_forgot_email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

        # Collapsible Developer / Admin Setup Notice
        st.write("")
        with st.expander("ℹ️ Developer / Administrator Notice (Instant Registration & Login)", expanded=False):
            st.markdown("""
            **Instant Registration & Email Verification in Supabase:**
            - **Why Email Verification Happens**: By default, Supabase sends confirmation emails and prevents password login until the link is clicked.
            - **How to Enable Instant Registration & Login (No Emails Required)**:
              1. Open your [Supabase Dashboard](https://app.supabase.com).
              2. Go to **Authentication** -> **Providers** -> **Email**.
              3. Turn **"Confirm email"** to **OFF** and click **Save**.
              *(New student accounts will now register instantly, receive an immediate session, and log in with password without requiring any email confirmation link).*
            - **Verifying Existing Accounts**: To confirm an already registered email, go to **Authentication** -> **Users**, click the `...` menu next to their email, and select **Confirm email**.
            """)

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
user_name = current_user.get("full_name") or user_email.split("@")[0].capitalize()
st.sidebar.markdown(f"""
<div class="user-session-card">
    <div class="user-badge">Signed In</div>
    <div class="user-name" style="font-weight: 600; color: #F5EFE6; margin-top: 4px;">{user_name}</div>
    <div class="user-email" style="font-size: 0.82rem; color: #BFAAB2;">{user_email}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Sign Out", type="secondary", use_container_width=True):
    supabase_auth.sign_out(access_token)
    session_token = st.query_params.get("session")
    if session_token:
        database.delete_user_session(session_token)
    st.query_params.clear()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.divider()

# Load user-specific profile from database (scoped to user_id)
user_profile = database.get_user_profile(user_id, access_token)
saved_skills_input = user_profile.get("skills_input", "")
saved_target_role = user_profile.get("target_group")
if not saved_target_role or saved_target_role in ["All Roles", "Fresher Only"]:
    saved_target_role = career_roles.DEFAULT_ROLE

saved_category = career_roles.get_category_for_role(saved_target_role)
category_keys = list(career_roles.CAREER_CATEGORIES.keys())
cat_index = category_keys.index(saved_category) if saved_category in category_keys else 0

# Sidebar: Profile Settings
st.sidebar.markdown("### Target Career Settings")
st.sidebar.caption("Benchmark your skillset against verified technical roles.")

selected_category = st.sidebar.selectbox(
    "Target Career Category",
    options=category_keys,
    index=cat_index,
    help="Select a technical domain to browse available career paths."
)

roles_in_cat = career_roles.CAREER_CATEGORIES[selected_category]
role_index = roles_in_cat.index(saved_target_role) if saved_target_role in roles_in_cat else 0

selected_role = st.sidebar.selectbox(
    "Target Career Role",
    options=roles_in_cat,
    index=role_index,
    help="Select the specific technical role to benchmark against."
)

group_selector = selected_role

skills_input = st.sidebar.text_area(
    "Current Technical Skills:",
    value=saved_skills_input,
    height=130,
    placeholder="e.g. Python, SQL, HTML, React, Docker",
    help="Type your current technical skills separated by commas."
)

analyze_button = st.sidebar.button("Analyze", type="primary")

clean_skills = skills_input.strip() if skills_input else ""
is_skills_empty = len(clean_skills) == 0

# Stale analysis invalidation:
# If user cleared the input, immediately invalidate previous results
if is_skills_empty:
    if st.session_state.get("analysis_results") is not None or saved_skills_input != "":
        st.session_state["analysis_results"] = None
        database.clear_gap_analysis(user_id)
        database.save_user_profile(user_id, group_selector, "", has_analyzed=False, access_token=access_token)
else:
    # If the user changed the skills or role in the UI without clicking Analyze,
    # invalidate old stale analysis so we do not display mismatched results!
    curr_res = st.session_state.get("analysis_results")
    if curr_res is not None:
        res_skills = curr_res.get("skills_input", "").strip()
        res_group = curr_res.get("group_name", "")
        if res_skills != clean_skills or res_group != group_selector:
            st.session_state["analysis_results"] = None
            st.sidebar.info("💡 Skills or career role modified. Click **Analyze** to generate your updated Gap Analysis.")

# Analyze button trigger
if analyze_button:
    if is_skills_empty:
        st.sidebar.warning("⚠️ Please enter at least one technical skill before analyzing.")
        st.session_state["analysis_results"] = None
        database.clear_gap_analysis(user_id)
        database.save_user_profile(user_id, group_selector, "", has_analyzed=False, access_token=access_token)
    else:
        # Load raw dataset for market demand calculations if available
        try:
            job_df = pd.read_csv("job_dataset.csv")
        except Exception:
            job_df = None

        # Run role-specific gap analysis and roadmap generation
        analysis_data = career_roles.analyze_role_skill_gap(
            role_name=group_selector,
            user_skills_input=clean_skills,
            job_df=job_df
        )

        gap_results = analysis_data["gap_results"]
        main_roadmap = analysis_data["main_roadmap"]
        optional_roadmap = analysis_data["optional_roadmap"]
        staged_curriculum = analysis_data["staged_curriculum"]

        roadmap_fallback_skills = [
            item["skill"] for item in main_roadmap
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
            "category": selected_category,
            "gap_results": gap_results,
            "main_roadmap": main_roadmap,
            "optional_roadmap": optional_roadmap,
            "staged_curriculum": staged_curriculum,
            "matched_skills_detailed": analysis_data["matched_skills_detailed"],
            "missing_skills_detailed": analysis_data["missing_skills_detailed"],
            "unmet_prereqs": [item["skill"] for item in main_roadmap if item["is_unmet_prereq"]],
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

# If analysis results are restored from DB without staged_curriculum, compute it
results_data = st.session_state.get("analysis_results")
if results_data is not None and "staged_curriculum" not in results_data:
    try:
        job_df = pd.read_csv("job_dataset.csv")
    except Exception:
        job_df = None
    fresh_data = career_roles.analyze_role_skill_gap(
        role_name=results_data.get("group_name", group_selector),
        user_skills_input=results_data.get("skills_input", clean_skills),
        job_df=job_df
    )
    results_data["staged_curriculum"] = fresh_data["staged_curriculum"]
    results_data["matched_skills_detailed"] = fresh_data["matched_skills_detailed"]
    results_data["missing_skills_detailed"] = fresh_data["missing_skills_detailed"]

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
    optional_roadmap = results_data.get("optional_roadmap", [])
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
            <p>Please enter your current technical skills (e.g. <em>Python, SQL, HTML, React, Docker</em>) in the sidebar and click <strong>Analyze</strong> to perform your skill gap analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    elif results_data is not None:
        role_desc = gap_results.get("description", "")
        role_cat = gap_results.get("category", selected_category)

        st.markdown(f"""
        <div class="career-role-header">
            <span class="role-category-badge">{role_cat}</span>
            <h3>{selected_group}</h3>
            <p>{role_desc}</p>
        </div>
        """, unsafe_allow_html=True)

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
        st.progress(progress_val, text=f"{selected_group} Market Alignment: {coverage_score:.1f}%")

        # Skill Level Distribution Pills
        matched_details = results_data.get("matched_skills_detailed", [])
        missing_details = results_data.get("missing_skills_detailed", [])
        all_details = matched_details + missing_details
        beginner_count = sum(1 for s in all_details if s.get("level") == "Beginner")
        interm_count = sum(1 for s in all_details if s.get("level") == "Intermediate")
        adv_count = sum(1 for s in all_details if s.get("level") == "Advanced")

        st.markdown(f"""
        <div class="chart-highlight-strip">
            <div class="chart-highlight-pill">Beginner Foundations: <strong>{beginner_count} Skills</strong></div>
            <div class="chart-highlight-pill">Intermediate Core: <strong>{interm_count} Skills</strong></div>
            <div class="chart-highlight-pill">Advanced & Systems: <strong>{adv_count} Skills</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        col_have, col_missing = st.columns(2)

        with col_have:
            st.markdown("#### Matched Competencies (Skills You Have)")
            if matched_details:
                for s in matched_details:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**✓ {s['display_name']}**")
                            st.caption(f"Stage: {s['stage']} · Level: {s['level']}")
                        with c2:
                            st.markdown(":green-background[**Mastered**]")
                            res_title, res_url = career_roles.get_skill_resource(s['skill'])
                            st.link_button("Docs ↗", res_url, help=res_title)
            elif gap_results["matched_skills"]:
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
                st.info(f"None of your entered skills match the requirements for {selected_group}.")

        with col_missing:
            st.markdown("#### Missing Required Competencies (Skills to Learn)")
            if missing_details:
                for s in missing_details:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**⚡ {s['display_name']}**")
                            st.caption(f"Stage: {s['stage']} · Level: {s['level']} · Demand: {s['demand_pct']:.1f}%")
                            st.markdown(f"<span style='font-size:0.8rem; color:#BFAAB2;'>{s['why_matters']}</span>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(":orange-background[**To Learn**]")
                            res_title, res_url = career_roles.get_skill_resource(s['skill'])
                            st.link_button(f"Learn {s['display_name'].split()[0]} ↗", res_url, help=f"Open {res_title}")
            elif gap_results["missing_skills"]:
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
                st.success(f"Incredible! You have mastered all core skills for {selected_group}.")

        st.divider()
        st.markdown("#### Typed Skills Outside This Career Profile")
        if gap_results["not_in_dataset"]:
            st.caption("The following skills you entered are not required for this role or not found in the technical taxonomy:")
            cols_unknown = st.columns(min(4, len(gap_results["not_in_dataset"])))
            for idx, skill in enumerate(gap_results["not_in_dataset"]):
                with cols_unknown[idx % len(cols_unknown)]:
                    st.info(f"🔍 **{format_skill_name(skill)}**")
        else:
            st.caption("All typed skills were recognized in the technical competency taxonomy.")
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
        st.subheader(f"Personalized Learning Journey — {selected_group}")
        st.caption("Structured progression: Foundational prerequisites precede advanced core skills, organized into clear learning phases.")

        core_count = len(main_roadmap)
        matched_count = gap_results["matched_count"]
        total_skills_count = gap_results["total_top"]

        st.markdown(f"""
        <div class="chart-highlight-strip">
            <div class="chart-highlight-pill">Target Career: <strong>{selected_group}</strong></div>
            <div class="chart-highlight-pill">Mastered: <strong>{matched_count} / {total_skills_count} Skills</strong></div>
            <div class="chart-highlight-pill">Remaining to Learn: <strong>{core_count} Milestones</strong></div>
        </div>
        """, unsafe_allow_html=True)

        if learning_progress["has_schedule"]:
            st.markdown(f"#### 🏆 Learning Journey Progress: {learning_progress['progress_pct']:.1f}% Mastered")
            st.progress(
                learning_progress["progress_pct"] / 100.0,
                text=f"{learning_progress['completed_tasks']} of {learning_progress['total_tasks']} tasks completed ({learning_progress['completed_hours']:.1f} / {learning_progress['total_hours']:.1f} hrs)"
            )
            st.write("")

        staged_curriculum = results_data.get("staged_curriculum")
        if not staged_curriculum:
            fresh_role = career_roles.get_role_data(selected_group)
            staged_curriculum = {
                "Foundations": [s for s in fresh_role["skills"] if s["stage"] == "Foundations"],
                "Core Skills": [s for s in fresh_role["skills"] if s["stage"] == "Core Skills"],
                "Advanced Skills": [s for s in fresh_role["skills"] if s["stage"] == "Advanced Skills"],
                "Projects & Specialization": [s for s in fresh_role["skills"] if s["stage"] == "Projects & Specialization"],
            }

        stage_meta = [
            ("Foundations", "🏗️ Phase 1: Foundations & Prerequisites", "Core principles, languages, and baseline tools required before advanced development."),
            ("Core Skills", "⚡ Phase 2: Core Engineering Competencies", "Primary engineering frameworks, databases, and day-to-day technologies."),
            ("Advanced Skills", "🚀 Phase 3: Advanced Specializations & Systems", "High-performance architecture, security, scaling, and cloud deployment."),
            ("Projects & Specialization", "💼 Phase 4: Capstone Projects & Production Deployment", "End-to-end hands-on projects, real-world systems, and production pipelines."),
        ]

        step_counter = 1
        for stage_key, stage_title, stage_desc in stage_meta:
            stage_items = staged_curriculum.get(stage_key, [])
            if not stage_items:
                continue

            st.markdown(f"""
            <div class="stage-section-header">
                <div>
                    <h4>{stage_title}</h4>
                    <span style="font-size:0.8rem; color:#BFAAB2;">{stage_desc}</span>
                </div>
                <span class="stage-pill">{len(stage_items)} Topics</span>
            </div>
            """, unsafe_allow_html=True)

            for item in stage_items:
                clean_skill_key = item["skill"].lower().strip()
                skill_stat = learning_progress["skill_progress"].get(clean_skill_key)
                is_known = item.get("is_matched", False)

                display_name = item.get("display_name", format_skill_name(item["skill"]))
                res_title = item.get("resource_title") or f"{display_name} Official Documentation"
                res_url = item.get("resource_url") or career_roles.get_skill_resource(clean_skill_key)[1]
                why_matters = item.get("why_matters", f"Essential competency for {selected_group}.")
                practice_proj = item.get("practice_project", f"Build a hands-on project demonstrating {display_name}.")
                prereqs = item.get("prerequisites", [])

                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"**Step {step_counter:02d}: {display_name}**")
                        st.markdown(f"<span style='font-size:0.82rem; color:#D6B875;'>Level: {item.get('level', 'Intermediate')}</span> · <span style='font-size:0.82rem; color:#BFAAB2;'>Demand: {item.get('demand_pct', 75.0):.1f}%</span>", unsafe_allow_html=True)

                        st.markdown(f"💡 **Why this matters for {selected_group}:** {why_matters}")

                        if prereqs:
                            formatted_prereqs = ", ".join(format_skill_name(p) for p in prereqs)
                            st.markdown(f"🔗 **Prerequisites:** {formatted_prereqs}")
                        else:
                            st.markdown(f"🔗 **Prerequisites:** *None (Foundational Entry Point)*")

                        st.markdown(f"""
                        <div class="practice-project-box">
                            🛠️ <strong>Suggested Practice / Mini-Project:</strong> {practice_proj}
                        </div>
                        """, unsafe_allow_html=True)

                        st.caption(f"📖 {res_title}")

                    with col_action:
                        # Status badge
                        if is_known:
                            st.markdown(":green-background[**✓ Mastered**]")
                        elif skill_stat and skill_stat.get("is_complete"):
                            st.markdown(":green-background[**✓ Mastered**]")
                        elif skill_stat and skill_stat.get("completed_tasks", 0) > 0:
                            st.markdown(f":violet-background[**In Progress ({skill_stat['pct']:.0f}%)**]")
                        else:
                            st.markdown(":orange-background[**To Learn**]")

                        st.link_button(f"Learn {display_name.split()[0]} ↗", res_url, use_container_width=True)

                step_counter += 1
    else:
        render_empty_state("Personalized Learning Journey")

# =========================================================================
# TAB 3: MARKET DEMAND
# =========================================================================
with tab_demand:
    if results_data is not None:
        st.subheader(f"Top In-Demand Skills — {selected_group}")
        st.caption(f"Market demand frequency and relative priority benchmarks for the {selected_group} career track.")

        top_skills = gap_results["group_demand"][:15]
        top_skill_name = format_skill_name(top_skills[0][0])
        top_skill_pct = top_skills[0][2]
        avg_demand_pct = sum(item[2] for item in top_skills) / len(top_skills)

        st.markdown(f"""
        <div class="chart-highlight-strip">
            <div class="chart-highlight-pill">Highest Market Demand: <strong>{top_skill_name} ({top_skill_pct:.1f}%)</strong></div>
            <div class="chart-highlight-pill">Average Priority Benchmark: <strong>{avg_demand_pct:.1f}%</strong></div>
            <div class="chart-highlight-pill">Target Career Track: <strong>{selected_group}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        chart_df = pd.DataFrame({
            "Skill": [format_skill_name(item[0]) for item in top_skills],
            "Demand (%)": [item[2] for item in top_skills]
        }).set_index("Skill")

        st.bar_chart(chart_df, color="#D6B875", height=420)

        st.markdown("#### Demand & Learning Resource Breakdown")
        for idx, item in enumerate(top_skills, start=1):
            s_name = item[0]
            s_pct = item[2]
            res_title, res_url = career_roles.get_skill_resource(s_name)
            with st.container(border=True):
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.markdown(f"**#{idx} · {format_skill_name(s_name)}** · **{s_pct:.1f}% Demand**")
                    st.caption(f"📖 {res_title}")
                with col_d2:
                    st.link_button(f"Learn {format_skill_name(s_name).split()[0]} ↗", res_url, use_container_width=True)
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

    # =========================================================================
    # ARIS INTELLIGENT ASSISTANT (Jarvis-Inspired Futuristic UI & Backend)
    # =========================================================================
    assistant_config = database.get_assistant_settings(user_id)
    assistant_name = assistant_config.get("assistant_name", "Aris")
    avatar_type = assistant_config.get("avatar_type", "aris_nexus")
    assistant_avatar_path = assistant_config.get("avatar_image_path", "avatars/aris_nexus.png")
    custom_avatar_path = assistant_config.get("custom_avatar_path")

    # Retrieve real AI engine connection status
    engine_type, engine_title, engine_desc = aris_assistant.get_ai_engine_status()

    # ARIS Header Card
    col_av, col_info = st.columns([1, 8])
    with col_av:
        if os.path.exists(assistant_avatar_path):
            st.image(assistant_avatar_path, width=64)
    with col_info:
        st.markdown(f"""
        <div class="aris-header-title-row">
            <span class="aris-display-name">{assistant_name}</span>
            <span class="aris-status-badge"><span class="aris-status-dot"></span>{engine_title}</span>
        </div>
        <p class="aris-header-subtitle">Composed, intelligent personal assistant for programming concepts, code debugging, and strategic roadmap progression.</p>
        """, unsafe_allow_html=True)

    # Assistant Profile Customization Section
    with st.expander(f"⚙️ Customize Assistant Profile ({assistant_name})", expanded=False):
        col_cust, col_prev = st.columns([3, 2])

        with col_cust:
            st.markdown("##### Assistant Identity & Appearance")
            cust_name = st.text_input(
                "Display Name:",
                value=assistant_name,
                placeholder="e.g. Aris, Jarvis, Nexus",
                help="Change the name your assistant uses in the conversation."
            )

            avatar_options = {
                "aris_nexus": "Aris Nexus (Regal Gold)",
                "quantum_arc": "Quantum Arc (Cyan Cyber)",
                "neural_pulse": "Neural Pulse (Rose Wine)",
                "titan_monolith": "Titan Monolith (Obsidian)",
                "custom": "Upload Custom Image",
            }
            avatar_keys = list(avatar_options.keys())
            def_idx = avatar_keys.index(avatar_type) if avatar_type in avatar_keys else 0

            selected_avatar_key = st.selectbox(
                "Choose Avatar Preset:",
                options=avatar_keys,
                format_func=lambda k: avatar_options[k],
                index=def_idx,
                help="Select a sleek futuristic avatar or upload your own."
            )

            saved_custom_path = custom_avatar_path
            if selected_avatar_key == "custom":
                uploaded_avatar = st.file_uploader(
                    "Upload Custom Profile Picture:",
                    type=["png", "jpg", "jpeg"],
                    help="Upload a square PNG or JPG image."
                )
                if uploaded_avatar is not None:
                    os.makedirs("avatars", exist_ok=True)
                    saved_custom_path = f"avatars/custom_{user_id}.png"
                    with open(saved_custom_path, "wb") as f_out:
                        f_out.write(uploaded_avatar.getbuffer())

            btn_save_col, btn_reset_col = st.columns(2)
            with btn_save_col:
                if st.button("Save Preferences", type="primary", use_container_width=True):
                    database.save_assistant_settings(
                        user_id=user_id,
                        assistant_name=cust_name.strip() or "Aris",
                        avatar_type=selected_avatar_key,
                        custom_avatar_path=saved_custom_path
                    )
                    st.success("Assistant profile saved.")
                    st.rerun()

            with btn_reset_col:
                if st.button("Reset to Defaults", type="secondary", use_container_width=True):
                    database.reset_assistant_settings(user_id)
                    st.info("Assistant profile reset to original Aris defaults.")
                    st.rerun()

        with col_prev:
            st.markdown("##### Real-Time Preview")
            # Determine preview image path
            if selected_avatar_key == "custom" and saved_custom_path and os.path.exists(saved_custom_path):
                prev_img_path = saved_custom_path
            elif selected_avatar_key in database.AVATAR_MAP and os.path.exists(database.AVATAR_MAP[selected_avatar_key]):
                prev_img_path = database.AVATAR_MAP[selected_avatar_key]
            else:
                prev_img_path = "avatars/aris_nexus.png"

            with st.container(border=True):
                col_p_img, col_p_txt = st.columns([1, 2])
                with col_p_img:
                    if os.path.exists(prev_img_path):
                        st.image(prev_img_path, width=70)
                with col_p_txt:
                    st.markdown(f"**{cust_name.strip() or 'Aris'}**")
                    st.caption("Active Personal Assistant")
                    st.caption(avatar_options.get(selected_avatar_key, "Preset"))

                st.markdown(
                    f"""
                    <div style="background: #2D0F1C; border-left: 3px solid #D6B875; border-radius: 6px; padding: 10px 12px; font-size: 0.82rem; color: #F5EFE6; margin-top: 8px;">
                        <span style="font-size: 0.72rem; text-transform: uppercase; color: #D6B875; font-weight: 600; display: block; margin-bottom: 3px;">Persona Preview</span>
                        <em>"Good day. I am {cust_name.strip() or 'Aris'}. How may I assist your engineering study today?"</em>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")

    # Chat Header with Clear Conversation Action
    col_chat_title, col_chat_clear = st.columns([5, 1])
    with col_chat_title:
        st.markdown(f"#### 💬 Conversation with {assistant_name}")
        st.caption("Ask technical questions, request code debugging, or explore your personalized curriculum.")
    with col_chat_clear:
        if st.button("Clear Chat", type="secondary", help="Clear conversation history"):
            database.clear_chat_history(user_id)
            st.session_state["chat_messages"] = []
            st.rerun()

    # Dedicated container for unified chat messages (prevents duplicate response boxes)
    chat_container = st.container()
    with chat_container:
        for msg in (st.session_state.get("chat_messages") or []):
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar=assistant_avatar_path):
                    st.markdown(f"**{assistant_name}**")
                    st.markdown(msg["content"])
            else:
                with st.chat_message("user"):
                    st.markdown(msg["content"])

    # Chat input
    user_query = st.chat_input(f"Ask {assistant_name} (e.g. 'What is NumPy?', 'Write Python code to create a Seaborn bar chart.')...")
    if user_query:
        if st.session_state.get("chat_messages") is None:
            st.session_state["chat_messages"] = []

        # Record user query in session state and persistent storage
        st.session_state["chat_messages"].append({"role": "user", "content": user_query})
        database.save_chat_message(user_id, "user", user_query)

        # Assemble schedule context
        sched_context = None
        if st.session_state.get("schedule_results") is not None:
            sr = st.session_state["schedule_results"]
            sched_context = (sr["weeks"], sr["total_weeks"], sr["hours_per_day"], sr["days_per_week"])

        # Display query and synthesize response in chat_container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant", avatar=assistant_avatar_path):
                st.markdown(f"**{assistant_name}**")
                with st.spinner(f"{assistant_name} is synthesizing response..."):
                    reply = aris_assistant.get_aris_response(
                        query=user_query,
                        chat_history=st.session_state["chat_messages"][:-1],
                        assistant_name=assistant_name,
                        analysis_results=st.session_state.get("analysis_results"),
                        schedule_context=sched_context,
                        user_profile=user_profile,
                    )
                st.markdown(reply)

        # Record assistant reply and cleanly rerun to synchronize state
        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        database.save_chat_message(user_id, "assistant", reply)
        st.rerun()

    st.markdown("---")
    st.caption(f"{assistant_name} · Inspired by Jarvis · Built for SkillBridge · {engine_desc}")

# Footer
st.markdown("---")
st.caption("Prototype on a public job-description dataset; results are indicative.")

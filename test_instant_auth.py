# test_instant_auth.py - End-to-end verification of TEST A through TEST G
import uuid
import database
import supabase_auth

def run_tests():
    print("==================================================")
    print("STARTING TEST A THROUGH TEST G AUTHENTICATION SUITE")
    print("==================================================")

    # Clean test database
    database.init_db()

    email_user1 = f"student_{uuid.uuid4().hex[:8]}@example.com"
    pass_user1 = "SecureKey2026!"
    name_user1 = "Alex Morgan"

    email_user2 = f"student_{uuid.uuid4().hex[:8]}@example.com"
    pass_user2 = "Developer2026!"
    name_user2 = "Sarah Connor"

    # ----------------------------------------------------
    # TEST A: Instant Account Registration Without Email Verification
    # ----------------------------------------------------
    print("\n[TEST A] Instant Account Registration")
    ok_a, msg_a, user_a = supabase_auth._local_sign_up(email_user1, pass_user1, full_name=name_user1)
    assert ok_a, f"Registration failed: {msg_a}"
    assert user_a is not None, "Expected user object"
    assert user_a["email"] == email_user1
    assert user_a["full_name"] == name_user1
    assert "access_token" in user_a and user_a["access_token"]
    assert not user_a.get("pending_verification"), "Instant registration must not have pending verification"
    user_id_1 = user_a["id"]

    # Save initial profile & workspace data for User 1
    database.save_user_profile(
        user_id_1,
        full_name=name_user1,
        target_group="Machine Learning Engineer",
        skills_input="Python, SQL, Pandas, Scikit-Learn",
        has_analyzed=True
    )
    database.save_gap_analysis(
        user_id_1,
        skills_input="Python, SQL, Pandas, Scikit-Learn",
        group_name="Machine Learning Engineer",
        gap_results={"coverage_percentage": 75.0, "matched_count": 6, "total_top": 8},
        main_roadmap=[{"skill": "PyTorch", "level": "Intermediate", "hours": 20}],
        optional_roadmap=[]
    )
    weeks_sample = [{
        "week_num": 1,
        "label": "Week 1",
        "days": [{
            "date_str": "2026-11-10",
            "tasks_str": "PyTorch (2h)"
        }]
    }]
    database.save_study_schedule(user_id_1, weeks=weeks_sample, total_weeks=1, hours_per_day=2.0, days_per_week=5, start_date="2026-11-10")
    tasks_initial = database.get_all_tasks(user_id_1)
    if tasks_initial:
        database.set_task_status(user_id_1, tasks_initial[0]["task_id"], True)
    print(f"[PASS] TEST A: User 1 ({email_user1}) registered instantly with access token and initial profile.")

    # ----------------------------------------------------
    # TEST B: Logout & Sign In Again with Exact Same Credentials
    # ----------------------------------------------------
    print("\n[TEST B] Logout & Re-authentication with Exact Credentials")
    supabase_auth.sign_out(user_a["access_token"])

    ok_b, msg_b, user_b = supabase_auth._local_sign_in(email_user1, pass_user1)
    assert ok_b, f"Login failed for valid credentials: {msg_b}"
    assert user_b["id"] == user_id_1
    assert user_b["email"] == email_user1
    assert user_b["full_name"] == name_user1
    print(f"[PASS] TEST B: Successfully authenticated User 1 with valid credentials.")

    # ----------------------------------------------------
    # TEST C: Refresh/Reopen Application & Session Restoration
    # ----------------------------------------------------
    print("\n[TEST C] Session Persistence Across Page Refreshes / Reopening")
    # Generate persistent session token
    session_token = database.create_user_session(user_b)
    assert session_token, "Session token generation failed"

    # Simulate reopening app with query param / session token
    restored = database.get_user_session(session_token)
    assert restored is not None, "Failed to restore session from token"
    assert restored["id"] == user_id_1
    assert restored["email"] == email_user1
    assert restored["full_name"] == name_user1
    print(f"[PASS] TEST C: Authenticated session successfully restored from token.")

    # ----------------------------------------------------
    # TEST D: Create Second Account with Different Email (Workspace Isolation)
    # ----------------------------------------------------
    print("\n[TEST D] Second Account Registration & Workspace Isolation")
    ok_d, msg_d, user_d = supabase_auth._local_sign_up(email_user2, pass_user2, full_name=name_user2)
    assert ok_d, f"Registration of user 2 failed: {msg_d}"
    user_id_2 = user_d["id"]
    assert user_id_2 != user_id_1

    # Verify User 2 has an independent, empty profile
    profile_u2 = database.get_user_profile(user_id_2)
    assert profile_u2["skills_input"] == "", f"User 2 should have empty skills, got: {profile_u2['skills_input']}"
    assert database.get_saved_gap_analysis(user_id_2) is None, "User 2 must not see User 1's gap analysis"
    assert database.get_saved_study_schedule(user_id_2) is None, "User 2 must not see User 1's schedule"
    assert len(database.get_all_tasks(user_id_2)) == 0, "User 2 must not see User 1's tasks"
    print(f"[PASS] TEST D: User 2 received a completely separate, clean workspace.")

    # ----------------------------------------------------
    # TEST E: Log Out & Sign Back into First Account (Data Preservation)
    # ----------------------------------------------------
    print("\n[TEST E] Preserved User Data on Sign In")
    supabase_auth.sign_out(user_d["access_token"])

    ok_e, msg_e, login_u1 = supabase_auth._local_sign_in(email_user1, pass_user1)
    assert ok_e, f"Relogin to User 1 failed: {msg_e}"
    assert login_u1["id"] == user_id_1

    # Load User 1's saved data
    profile_u1 = database.get_user_profile(user_id_1)
    assert profile_u1["skills_input"] == "Python, SQL, Pandas, Scikit-Learn"
    assert profile_u1["target_group"] == "Machine Learning Engineer"

    gap_u1 = database.get_saved_gap_analysis(user_id_1)
    assert gap_u1 is not None
    assert gap_u1["group_name"] == "Machine Learning Engineer"
    assert gap_u1["gap_results"]["coverage_percentage"] == 75.0

    schedule_u1 = database.get_saved_study_schedule(user_id_1)
    assert schedule_u1 is not None
    assert schedule_u1["total_weeks"] == 1

    tasks_u1 = database.get_all_tasks(user_id_1)
    assert len(tasks_u1) == 1
    assert tasks_u1[0]["skill"] == "PyTorch"
    assert tasks_u1[0]["is_completed"] == 1

    prog_u1 = database.get_learning_progress(user_id_1)
    assert prog_u1["completed_tasks"] == 1
    assert prog_u1["total_tasks"] == 1
    assert prog_u1["progress_pct"] == 100.0
    print(f"[PASS] TEST E: User 1 original data, target role, roadmap, schedule, and task progress fully preserved.")

    # ----------------------------------------------------
    # TEST F: Incorrect Password Error Handling
    # ----------------------------------------------------
    print("\n[TEST F] Incorrect Password Error Handling")
    ok_f, msg_f, _ = supabase_auth._local_sign_in(email_user1, "CompletelyWrongPassword123")
    assert not ok_f, "Login with wrong password should fail"
    assert "invalid email or password" in msg_f.lower(), f"Expected friendly error message, got: {msg_f}"
    print(f"[PASS] TEST F: Incorrect password rejected with friendly message: '{msg_f}'")

    # ----------------------------------------------------
    # TEST G: Register Existing Email (Prevent Duplicates)
    # ----------------------------------------------------
    print("\n[TEST G] Register Existing Email Rejection")
    ok_g, msg_g, _ = supabase_auth._local_sign_up(email_user1, "SomeNewPassword999", full_name="Imposter")
    assert not ok_g, "Registering existing email should fail"
    assert ("already registered" in msg_g.lower() or "already exists" in msg_g.lower()), f"Expected already registered message, got: {msg_g}"
    print(f"[PASS] TEST G: Duplicate registration blocked with message: '{msg_g}'")

    print("\n==================================================")
    print("ALL TESTS (TEST A THROUGH TEST G) PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()

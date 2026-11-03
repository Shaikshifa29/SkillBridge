# verify_multi_tenant.py - Multi-User Isolation & Authentication Verification Suite
import os
import uuid
import datetime
import database
import supabase_auth
import module3_gap_analysis as m3
import module4_roadmap as m4
import planner

def test_multi_user_isolation():
    print("--- 1. Testing User Authentication ---")
    email_a = f"user_a_{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"user_b_{uuid.uuid4().hex[:6]}@example.com"
    pw = "SecretPassword123"

    ok_a, msg_a, user_a = supabase_auth.sign_up(email_a, pw)
    assert ok_a, f"Sign up A failed: {msg_a}"
    assert user_a and "id" in user_a, "User A object missing id"
    uid_a = user_a["id"]
    print(f"[PASS] User A created with id: {uid_a}")

    ok_b, msg_b, user_b = supabase_auth.sign_up(email_b, pw)
    assert ok_b, f"Sign up B failed: {msg_b}"
    assert user_b and "id" in user_b, "User B object missing id"
    uid_b = user_b["id"]
    print(f"[PASS] User B created with id: {uid_b}")

    # Verify duplicate email check
    dup_ok, dup_msg, _ = supabase_auth.sign_up(email_a, pw)
    assert not dup_ok, "Duplicate sign up should fail"
    print(f"[PASS] Duplicate email registration correctly prevented")

    # Verify sign in
    sin_ok, sin_msg, sin_user = supabase_auth.sign_in(email_a, pw)
    assert sin_ok and sin_user["id"] == uid_a, "Sign in A failed"
    print(f"[PASS] User A authentication verified")

    print("\n--- 2. Testing Clean Empty State for New User ---")
    sched_b_initial = database.get_saved_study_schedule(uid_b)
    assert sched_b_initial is None, "New user B must have NO initial schedule"
    prog_b_initial = database.get_learning_progress(uid_b)
    assert prog_b_initial["has_schedule"] is False, "New user B has_schedule must be False"
    assert prog_b_initial["total_tasks"] == 0, "New user B total_tasks must be 0"
    print(f"[PASS] User B workspace is completely clean and empty initially")

    print("\n--- 3. Testing User Profile & Analysis Isolation ---")
    skills_a = "Python, SQL, Scikit-Learn"
    skills_b = "TensorFlow, PyTorch, OpenCV"
    
    database.save_user_profile(uid_a, "All Roles", skills_a, has_analyzed=True)
    database.save_user_profile(uid_b, "Fresher Only", skills_b, has_analyzed=True)

    prof_a = database.get_user_profile(uid_a)
    prof_b = database.get_user_profile(uid_b)

    assert prof_a["skills_input"] == skills_a, "User A skills mismatch"
    assert prof_a["target_group"] == "All Roles", "User A target group mismatch"
    assert prof_b["skills_input"] == skills_b, "User B skills mismatch"
    assert prof_b["target_group"] == "Fresher Only", "User B target group mismatch"
    print(f"[PASS] User profile isolation verified (User A != User B)")

    # Run gap analysis for A and save
    gap_a = m3.run_module_3(skills_a, "1")
    main_a, opt_a, _ = m4.generate_roadmap_from_gap(gap_a)
    database.save_gap_analysis(uid_a, skills_a, "All Roles", gap_a, main_a, opt_a)

    # Gap analysis for B should still be None
    saved_gap_b = database.get_saved_gap_analysis(uid_b)
    assert saved_gap_b is None, "User B should have NO saved gap analysis yet"

    saved_gap_a = database.get_saved_gap_analysis(uid_a)
    assert saved_gap_a is not None, "User A saved gap analysis must exist"
    assert saved_gap_a["skills_input"] == skills_a
    print(f"[PASS] Gap analysis isolation verified")

    print("\n--- 4. Testing Study Schedule & Task Isolation ---")
    weeks_a, tot_w_a = planner.make_schedule(main_a + opt_a, 2.0, 5, datetime.date.today())
    database.save_study_schedule(uid_a, weeks_a, tot_w_a, 2.0, 5, datetime.date.today())

    # User A now has a schedule
    sched_a = database.get_saved_study_schedule(uid_a)
    assert sched_a is not None, "User A schedule must exist"
    assert len(sched_a["weeks"]) == tot_w_a

    # User B STILL has NO schedule!
    sched_b_check = database.get_saved_study_schedule(uid_b)
    assert sched_b_check is None, "User B must still have NO schedule! (Must not see User A's schedule)"
    print(f"[PASS] Study schedule isolation verified (User B cannot see User A's schedule)")

    print("\n--- 5. Testing Task Completion & Progress Isolation ---")
    tasks_a = database.get_all_tasks(uid_a)
    assert len(tasks_a) > 0, "User A must have tasks"
    first_task = tasks_a[0]["task_id"]

    # Mark first task complete for User A
    database.set_task_status(uid_a, first_task, True)

    prog_a = database.get_learning_progress(uid_a)
    assert prog_a["completed_tasks"] == 1, "User A completed_tasks should be 1"
    assert prog_a["progress_pct"] > 0.0, "User A progress_pct should be > 0"

    # User B progress should still be 0 tasks
    prog_b = database.get_learning_progress(uid_b)
    assert prog_b["completed_tasks"] == 0, "User B completed_tasks must be 0"
    assert prog_b["total_tasks"] == 0, "User B total_tasks must be 0"
    print(f"[PASS] Task completion & progress tracking isolation verified")

    print("\n--- 6. Testing Plan Reset Isolation ---")
    database.reset_study_plan(uid_a)
    sched_a_reset = database.get_saved_study_schedule(uid_a)
    assert sched_a_reset is None, "User A schedule should be None after reset"
    prog_a_reset = database.get_learning_progress(uid_a)
    assert prog_a_reset["total_tasks"] == 0, "User A tasks should be 0 after reset"
    print(f"[PASS] Reset study plan verified")

    print("\n--- 7. Testing Chat History Isolation ---")
    database.save_chat_message(uid_a, "user", "What is numpy?")
    database.save_chat_message(uid_a, "assistant", "NumPy is the foundational array library.")
    database.save_chat_message(uid_b, "user", "What is PyTorch?")

    chat_a = database.get_chat_history(uid_a)
    chat_b = database.get_chat_history(uid_b)

    assert len(chat_a) == 2, f"Chat A length should be 2, got {len(chat_a)}"
    assert len(chat_b) == 1, f"Chat B length should be 1, got {len(chat_b)}"
    assert chat_a[0]["content"] == "What is numpy?"
    assert chat_b[0]["content"] == "What is PyTorch?"
    print(f"[PASS] Chat history isolation verified (User A != User B)")

    print("\n--- 8. Testing Stale Analysis Invalidation Logic ---")
    # Empty string should clear gap analysis
    database.save_user_profile(uid_a, "All Roles", "", has_analyzed=False)
    database.clear_gap_analysis(uid_a)
    cleared_gap = database.get_saved_gap_analysis(uid_a)
    assert cleared_gap is None, "Cleared gap analysis should return None"
    prof_cleared = database.get_user_profile(uid_a)
    assert prof_cleared["skills_input"] == "", "Profile skills_input should be empty"
    assert prof_cleared["has_analyzed"] is False, "has_analyzed should be False"
    print(f"[PASS] Stale analysis cleared correctly on empty input")

    print("\n=======================================================")
    print("ALL MULTI-USER ISOLATION & AUTHENTICATION TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    test_multi_user_isolation()


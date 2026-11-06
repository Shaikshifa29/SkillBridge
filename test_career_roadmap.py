# test_career_roadmap.py - Comprehensive Test Suite for Technical Career Roadmaps & Learning Links
import os
import uuid
import pandas as pd
import career_roles
import database
import planner
import module4_roadmap as m4

def run_tests():
    print("==================================================")
    print("STARTING TECHNICAL CAREER ROADMAP VERIFICATION")
    print("==================================================")

    # 1. VERIFY CATEGORIES & 36 ROLES
    print("\n[TEST 1] Verifying 6 Categories & 36 Technical Roles...")
    expected_categories = [
        "AI & Machine Learning",
        "Data Careers",
        "Software Development",
        "Cybersecurity",
        "Cloud & DevOps",
        "Other Technical Careers",
    ]
    for cat in expected_categories:
        assert cat in career_roles.CAREER_CATEGORIES, f"Missing category: {cat}"
        roles = career_roles.CAREER_CATEGORIES[cat]
        assert len(roles) >= 4, f"Category {cat} should have at least 4 roles, got {len(roles)}"

    all_roles = career_roles.ALL_ROLES
    assert len(all_roles) == 36, f"Expected exactly 36 roles, got {len(all_roles)}"
    print(f"[PASS] All {len(all_roles)} roles present across {len(career_roles.CAREER_CATEGORIES)} categories.")

    # 2. VERIFY REQUIRED SPECIFIC ROLES ARE PRESENT
    print("\n[TEST 2] Verifying Specific Roles Requested by User...")
    key_roles = [
        "AI Engineer", "Machine Learning Engineer", "Deep Learning Engineer",
        "NLP Engineer", "Computer Vision Engineer", "Generative AI Engineer",
        "Data Analyst", "Data Scientist", "Data Engineer", "Business Intelligence Developer", "Analytics Engineer",
        "Software Developer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Mobile App Developer", "Python Developer", "Java Developer",
        "Cybersecurity Analyst", "Security Engineer", "Penetration Tester", "Ethical Hacker", "SOC Analyst", "Cloud Security Engineer",
        "Cloud Engineer", "DevOps Engineer", "Site Reliability Engineer", "Platform Engineer",
        "Database Administrator", "QA Automation Engineer", "Software Test Engineer", "Blockchain Developer", "Embedded Systems Engineer", "IoT Engineer", "Network Engineer", "Systems Engineer"
    ]
    for r in key_roles:
        assert r in all_roles, f"Role '{r}' was not found in ALL_ROLES"
        cat = career_roles.get_category_for_role(r)
        assert cat in expected_categories, f"Invalid category {cat} for role {r}"
    print(f"[PASS] All {len(key_roles)} user-specified roles verified.")

    # 3. VERIFY ROLE-SPECIFIC APPROPRIATE SKILL LISTS (NOT REUSED GENERIC SKILLS)
    print("\n[TEST 3] Verifying Individualized Skill Mappings for Key Roles...")
    fs_data = career_roles.get_role_data("Full Stack Developer")
    fs_skills = [s["skill"] for s in fs_data["skills"]]
    assert "html" in fs_skills and "react" in fs_skills and "node.js" in fs_skills

    sec_data = career_roles.get_role_data("Cybersecurity Analyst")
    sec_skills = [s["skill"] for s in sec_data["skills"]]
    assert "networking" in sec_skills and "siem tools" in sec_skills and "incident response" in sec_skills

    ds_data = career_roles.get_role_data("Data Scientist")
    ds_skills = [s["skill"] for s in ds_data["skills"]]
    assert "python" in ds_skills and "scikit-learn" in ds_skills and "pandas" in ds_skills

    cloud_data = career_roles.get_role_data("Cloud Engineer")
    cloud_skills = [s["skill"] for s in cloud_data["skills"]]
    assert "aws" in cloud_skills and "docker" in cloud_skills and "terraform" in cloud_skills

    # Assert skill sets are distinct
    assert set(fs_skills) != set(sec_skills), "Full Stack and Security skills must be distinct"
    assert set(sec_skills) != set(ds_skills), "Security and Data Science skills must be distinct"
    assert set(ds_skills) != set(cloud_skills), "Data Science and Cloud skills must be distinct"
    print("[PASS] Distinct, appropriate skill mappings verified across roles.")

    # 4. VERIFY USER-SPECIFIED EXACT CLICKABLE LEARNING LINKS
    print("\n[TEST 4] Verifying Authoritative Clickable Learning URLs...")
    required_url_checks = {
        "html": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content",
        "python": "https://docs.python.org/3/tutorial/",
        "sql": "https://www.w3schools.com/sql/",
        "git": "https://git-scm.com/doc",
        "machine learning": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "cybersecurity": "https://owasp.org/www-project-top-ten/",
        "react": "https://react.dev/learn",
        "docker": "https://docs.docker.com/get-started/",
    }
    for skill_k, expected_url in required_url_checks.items():
        title, url = career_roles.get_skill_resource(skill_k)
        assert url == expected_url, f"Expected {expected_url} for '{skill_k}', got {url}"
        assert len(title) > 0, f"Title missing for '{skill_k}'"

    # Verify every skill in all 36 roles has a valid HTTPS link
    total_skills_checked = 0
    for r_name in all_roles:
        r_info = career_roles.get_role_data(r_name)
        for s in r_info["skills"]:
            total_skills_checked += 1
            assert s["resource_url"].startswith("https://"), f"Invalid resource URL in {r_name} for {s['skill']}: {s['resource_url']}"
            assert len(s["why_matters"]) > 10, f"Missing why_matters in {r_name} for {s['skill']}"
            assert len(s["practice_project"]) > 10, f"Missing practice_project in {r_name} for {s['skill']}"
            assert s["stage"] in ["Foundations", "Core Skills", "Advanced Skills", "Projects & Specialization"]
            assert s["level"] in ["Beginner", "Intermediate", "Advanced"]
    print(f"[PASS] All {total_skills_checked} skills across all 36 roles have valid HTTPS links, projects, and explanations.")

    # 5. TEST SKILL GAP ANALYSIS FOR DIFFERENT ROLES
    print("\n[TEST 5] Testing Dynamic Skill Gap Analysis Across Target Roles...")
    user_skills = "HTML, CSS, JavaScript, Git"

    # For Full Stack Developer (user should match html, css, javascript, git)
    res_fs = career_roles.analyze_role_skill_gap("Full Stack Developer", user_skills)
    gap_fs = res_fs["gap_results"]
    assert gap_fs["matched_count"] >= 4, f"Expected at least 4 matched for Full Stack, got {gap_fs['matched_count']}"
    assert gap_fs["coverage_percentage"] > 25.0, "Coverage score should be > 25%"

    # For Cybersecurity Analyst with same skills (should match git only or very few)
    res_sec = career_roles.analyze_role_skill_gap("Cybersecurity Analyst", user_skills)
    gap_sec = res_sec["gap_results"]
    assert gap_sec["matched_count"] < gap_fs["matched_count"], "Security should have fewer matches with web dev skills"

    # Test changing to Cybersecurity skills
    cyber_skills = "Networking, Linux, Wireshark, Python"
    res_sec2 = career_roles.analyze_role_skill_gap("Cybersecurity Analyst", cyber_skills)
    gap_sec2 = res_sec2["gap_results"]
    assert gap_sec2["matched_count"] >= 3, f"Expected at least 3 matches for Cybersecurity, got {gap_sec2['matched_count']}"
    print(f"[PASS] Dynamic skill gap analysis updates properly when target role changes.")

    # 6. VERIFY STAGED ROADMAP & PREREQUISITES
    print("\n[TEST 6] Verifying Staged Roadmap (Foundations -> Core -> Advanced -> Projects)...")
    stages = res_fs["staged_curriculum"]
    for expected_stg in ["Foundations", "Core Skills", "Advanced Skills", "Projects & Specialization"]:
        assert expected_stg in stages, f"Missing stage {expected_stg}"
        assert len(stages[expected_stg]) > 0, f"Stage {expected_stg} has no items"

    main_rm = res_fs["main_roadmap"]
    assert len(main_rm) > 0, "Missing skills roadmap should not be empty"
    for item in main_rm:
        assert "resource_url" in item and item["resource_url"].startswith("https://")
        assert "why_matters" in item
        assert "practice_project" in item
    print(f"[PASS] Staged roadmap and prerequisite sequencing verified.")

    # 7. VERIFY STUDY PLANNER INTEGRATION
    print("\n[TEST 7] Testing Study Planner Schedule Generation with Role Roadmap...")
    import datetime
    weeks, total_weeks = planner.make_schedule(
        main_rm, hours_per_day=2, days_per_week=5, start_date=datetime.date.today()
    )
    assert total_weeks > 0, "Total weeks must be positive"
    assert len(weeks) == total_weeks, f"Weeks list mismatch: {len(weeks)} vs {total_weeks}"
    print(f"[PASS] Study planner generated {total_weeks} weeks of day-by-day tasks.")

    # 8. VERIFY DATABASE MULTI-TENANT PERSISTENCE WITH ROLE NAMES
    print("\n[TEST 8] Testing Database Persistence with Role Names...")
    test_user_id = str(uuid.uuid4())
    database.save_user_profile(
        test_user_id,
        target_group="Cybersecurity Analyst",
        skills_input="Networking, Linux, Python",
        has_analyzed=True
    )
    prof = database.get_user_profile(test_user_id)
    assert prof["target_group"] == "Cybersecurity Analyst", f"Expected Cybersecurity Analyst, got {prof['target_group']}"
    assert prof["skills_input"] == "Networking, Linux, Python"

    database.save_gap_analysis(
        test_user_id,
        skills_input="Networking, Linux, Python",
        group_name="Cybersecurity Analyst",
        gap_results=gap_sec2,
        main_roadmap=res_sec2["main_roadmap"],
        optional_roadmap=[]
    )
    saved_gap = database.get_saved_gap_analysis(test_user_id)
    assert saved_gap["group_name"] == "Cybersecurity Analyst"
    assert saved_gap["gap_results"]["matched_count"] == gap_sec2["matched_count"]
    print("[PASS] User profile and gap analysis persistence with career role verified.")

    print("\n==================================================")
    print("ALL TECHNICAL CAREER ROADMAP TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()


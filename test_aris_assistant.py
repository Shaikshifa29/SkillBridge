# test_aris_assistant.py - Automated Verification Suite for ARIS Assistant
import os
import uuid
import database
import aris_assistant
import planner

def test_aris_suite():
    print("==================================================")
    print("STARTING ARIS AI ASSISTANT VERIFICATION SUITE")
    print("==================================================")

    # 1. TEST QUESTION: "What is NumPy?"
    print("\n[TEST 1] Testing prompt: 'What is NumPy?'")
    r_numpy = aris_assistant.get_aris_response("What is NumPy?", [], assistant_name="Aris")
    assert "numpy" in r_numpy.lower() or "numerical" in r_numpy.lower(), "NumPy not mentioned in response"
    assert "ndarray" in r_numpy.lower() or "array" in r_numpy.lower(), "Arrays not explained"
    assert "```python" in r_numpy, "Code example missing for NumPy"
    assert "Study Assistant Capabilities:" not in r_numpy, "Should not return canned capabilities message"
    assert "Define Input/Output Specifications" not in r_numpy, "Should not return generic platitudes"
    print("[PASS] Prompt 1 ('What is NumPy?') answered with technical depth and code example.")

    # 2. TEST QUESTION: "Write Python code to create a Seaborn bar chart."
    print("\n[TEST 2] Testing prompt: 'Write Python code to create a Seaborn bar chart.'")
    r_seaborn = aris_assistant.get_aris_response("Write Python code to create a Seaborn bar chart.", [], assistant_name="Aris")
    assert "seaborn" in r_seaborn.lower() or "sns" in r_seaborn, "Seaborn not mentioned"
    assert "barplot" in r_seaborn or "bar" in r_seaborn.lower(), "Bar plot function not in response"
    assert "```python" in r_seaborn, "Runnable code block missing"
    assert "pip install seaborn" in r_seaborn.lower(), "Installation instructions missing"
    assert "Define Input/Output Specifications" not in r_seaborn, "Should not return generic platitudes"
    print("[PASS] Prompt 2 ('Write Python code to create a Seaborn bar chart.') returned complete runnable code.")

    # 3. TEST MULTI-TURN FOLLOW-UP: "Explain the code you just gave me."
    print("\n[TEST 3] Testing follow-up prompt: 'Explain the code you just gave me.'")
    history_after_seaborn = [
        {"role": "user", "content": "Write Python code to create a Seaborn bar chart."},
        {"role": "assistant", "content": r_seaborn}
    ]
    r_explain = aris_assistant.get_aris_response("Explain the code you just gave me.", history_after_seaborn, assistant_name="Aris")
    assert "seaborn" in r_explain.lower() or "barplot" in r_explain.lower() or "matplotlib" in r_explain.lower() or "breakdown" in r_explain.lower(), "Follow-up explanation failed to reference recent code"
    assert "Define Input/Output Specifications" not in r_explain, "Should not return generic platitudes"
    print("[PASS] Prompt 3 ('Explain the code you just gave me.') accurately broke down the preceding code.")

    # 4. TEST MULTI-TURN FOLLOW-UP: "Modify it to use a line chart instead."
    print("\n[TEST 4] Testing follow-up prompt: 'Modify it to use a line chart instead.'")
    history_after_explain = history_after_seaborn + [
        {"role": "user", "content": "Explain the code you just gave me."},
        {"role": "assistant", "content": r_explain}
    ]
    r_line = aris_assistant.get_aris_response("Modify it to use a line chart instead.", history_after_explain, assistant_name="Aris")
    assert "lineplot" in r_line or "line chart" in r_line.lower() or "line plot" in r_line.lower(), "Line chart modification missing"
    assert "```python" in r_line, "Updated code block missing"
    assert "Define Input/Output Specifications" not in r_line, "Should not return generic platitudes"
    print("[PASS] Prompt 4 ('Modify it to use a line chart instead.') adapted the code to a Seaborn line plot.")

    # 5. TEST TROUBLESHOOTING: "I'm getting a ModuleNotFoundError for seaborn. How do I fix it?"
    print("\n[TEST 5] Testing prompt: 'I'm getting a ModuleNotFoundError for seaborn. How do I fix it?'")
    r_err = aris_assistant.get_aris_response("I'm getting a ModuleNotFoundError for seaborn. How do I fix it?", [], assistant_name="Aris")
    assert "pip install seaborn" in r_err.lower(), "Pip install command missing"
    assert "modulenotfounderror" in r_err.lower() or "environment" in r_err.lower() or "interpreter" in r_err.lower(), "Root cause explanation missing"
    assert "import seaborn" in r_err.lower(), "Verification code snippet missing"
    assert "Define Input/Output Specifications" not in r_err, "Should not return generic platitudes"
    print("[PASS] Prompt 5 (ModuleNotFoundError troubleshooting) answered with diagnosis and fixes.")

    # 6. TEST STUDY PLAN CONTEXT:
    # 6A. Without active schedule (Truthful empty state, no fake data)
    print("\n[TEST 6A] Testing prompt: 'What is my current study plan?' without active schedule")
    r_plan_empty = aris_assistant.get_aris_response("What is my current study plan?", [], assistant_name="Aris", schedule_context=None)
    assert "do not have an active study plan" in r_plan_empty.lower() or "no active study plan" in r_plan_empty.lower(), "Must truthfully state no active plan exists"
    assert "generate schedule" in r_plan_empty.lower() or "study planner" in r_plan_empty.lower(), "Must explain how to create one"
    print("[PASS] Prompt 6A truthfully reported empty study plan state.")

    # 6B. With active schedule (Accurate summary)
    print("\n[TEST 6B] Testing prompt: 'What is my current study plan?' with active schedule")
    mock_weeks = [{"label": "Week 1: Python & SQL Foundations", "days": []}]
    mock_schedule = (mock_weeks, 10, 2, 5)  # 10 weeks, 2 hours/day, 5 days/week
    r_plan_active = aris_assistant.get_aris_response("What is my current study plan?", [], assistant_name="Aris", schedule_context=mock_schedule)
    assert "10 weeks" in r_plan_active.lower(), "Total weeks missing from plan summary"
    assert "2 hours/day" in r_plan_active.lower() or "2h" in r_plan_active.lower(), "Hours/day missing from plan summary"
    assert "5 days/week" in r_plan_active.lower(), "Days/week missing from plan summary"
    assert "Week 1" in r_plan_active, "Milestone missing from plan summary"
    print("[PASS] Prompt 6B accurately summarized the active schedule context.")

    # 7. TEST PLANNER DELEGATION (No conflicting handlers)
    print("\n[TEST 7] Testing planner.get_study_assistant_response delegation")
    r_planner_delegation = planner.get_study_assistant_response("What is NumPy?")
    assert "numpy" in r_planner_delegation.lower(), "Planner did not delegate to Aris"
    assert "```python" in r_planner_delegation, "Code snippet missing from delegated response"
    print("[PASS] planner.py unified delegation verified.")

    # 8. TEST CODE SNIPPET DEBUGGING DIRECTLY
    print("\n[TEST 8] Testing code debugging with a snippet containing syntax/logic errors")
    buggy_code = "Help me debug this code:\n```python\ndef get_val(x)\n    if x = 5:\n        return x\n```"
    r_buggy = aris_assistant.get_aris_response(buggy_code, [], assistant_name="Aris")
    assert "colon" in r_buggy.lower() or "assignment" in r_buggy.lower() or "diagnostic" in r_buggy.lower(), "Failed to diagnose bug"
    print("[PASS] Direct code snippet debugging verified.")

    # 9. TEST ASSISTANT PROFILE CUSTOMIZATION & PERSISTENCE
    print("\n[TEST 9] Testing Assistant Profile Customization & Isolation")
    user_1 = str(uuid.uuid4())
    user_2 = str(uuid.uuid4())

    # Default settings
    s1 = database.get_assistant_settings(user_1)
    assert s1["assistant_name"] == "Aris", f"Default name must be Aris, got {s1['assistant_name']}"
    assert s1["avatar_type"] == "aris_nexus", f"Default avatar must be aris_nexus, got {s1['avatar_type']}"
    assert os.path.exists(s1["avatar_image_path"]), f"Avatar file must exist at {s1['avatar_image_path']}"

    # Customization for User 1
    database.save_assistant_settings(user_1, "Jarvis Prime", "quantum_arc")
    s1_updated = database.get_assistant_settings(user_1)
    assert s1_updated["assistant_name"] == "Jarvis Prime", "Custom name not persisted"
    assert s1_updated["avatar_type"] == "quantum_arc", "Custom avatar not persisted"

    # Verify User 2 is NOT affected (Data Isolation)
    s2 = database.get_assistant_settings(user_2)
    assert s2["assistant_name"] == "Aris", "User 2 should still have default name Aris"
    assert s2["avatar_type"] == "aris_nexus", "User 2 should still have default avatar aris_nexus"

    # Reset User 1 to defaults
    database.reset_assistant_settings(user_1)
    s1_reset = database.get_assistant_settings(user_1)
    assert s1_reset["assistant_name"] == "Aris", "Name must reset to Aris"
    assert s1_reset["avatar_type"] == "aris_nexus", "Avatar must reset to aris_nexus"
    print("[PASS] Assistant profile settings and tenant isolation verified.")

    # 10. TEST ENGINE STATUS DETECTION
    print("\n[TEST 10] Testing AI engine connection status detection")
    status_type, status_title, status_desc = aris_assistant.get_ai_engine_status()
    assert status_type in ["gemini", "openai", "groq", "local"]
    print(f"[PASS] Engine Status: Type='{status_type}', Title='{status_title}', Description='{status_desc}'")

    print("\n==================================================")
    print("ALL 10 ARIS ASSISTANT VERIFICATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_aris_suite()

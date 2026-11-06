# test_auth_flow.py - Comprehensive Authentication Verification Suite
import os
import re
import uuid
import supabase_auth

def test_auth_suite():
    print("==================================================")
    print("STARTING AUTHENTICATION VERIFICATION SUITE")
    print("==================================================")

    # 1. TEST INPUT SANITIZATION
    print("\n[TEST 1] Testing Email Sanitization & Normalization")
    dirty_email = "  \u00a0User.Name+Tag@Example.COM \u200b\t\n "
    clean = supabase_auth.sanitize_email(dirty_email)
    assert clean == "user.name+tag@example.com", f"Expected clean email, got '{clean}'"
    print(f"[PASS] Successfully stripped unicode, zero-width spaces, and normalized: '{clean}'")

    # 2. TEST EMAIL SYNTAX VALIDATION
    print("\n[TEST 2] Testing Email Regex Validation")
    valid_emails = [
        "john.doe@gmail.com",
        "alex+dev@company.co.uk",
        "student_123@university.edu",
    ]
    invalid_emails = [
        "notanemail",
        "@nodomain.com",
        "user@.com",
        "user@domain",
        "user space@domain.com",
        "",
    ]
    for em in valid_emails:
        assert supabase_auth.is_valid_email_format(em), f"Should be valid: {em}"
    for em in invalid_emails:
        assert not supabase_auth.is_valid_email_format(em), f"Should be invalid: {em}"
    print(f"[PASS] Correctly validated {len(valid_emails)} valid and {len(invalid_emails)} invalid email formats")

    # 3. TEST ERROR PARSING & MEANINGFUL MESSAGES
    print("\n[TEST 3] Testing Supabase Error Code Parsing")

    # Rate limit error
    msg_429 = supabase_auth._parse_supabase_error(429, {"code": 429, "msg": "Rate limit exceeded"}, "Default")
    assert "rate limit" in msg_429.lower(), f"Expected rate limit alert, got: {msg_429}"
    print(f"[PASS] Rate limit mapped correctly")

    # Email not confirmed error
    msg_unconfirmed = supabase_auth._parse_supabase_error(
        400,
        {"error": "invalid_grant", "error_description": "Email not confirmed"},
        "Default"
    )
    assert "email not confirmed" in msg_unconfirmed.lower(), f"Expected unconfirmed alert, got: {msg_unconfirmed}"
    print(f"[PASS] Email not confirmed mapped correctly")

    # Invalid credentials error
    msg_cred = supabase_auth._parse_supabase_error(
        400,
        {"error": "invalid_grant", "error_description": "Invalid login credentials"},
        "Default"
    )
    assert "invalid email or password" in msg_cred.lower(), f"Expected credential alert, got: {msg_cred}"
    print(f"[PASS] Invalid credentials mapped correctly")

    # User already registered error
    msg_dup = supabase_auth._parse_supabase_error(
        422,
        {"code": 422, "msg": "User already registered"},
        "Default"
    )
    assert "already registered" in msg_dup.lower(), f"Expected already registered alert, got: {msg_dup}"
    print(f"[PASS] Duplicate user mapped correctly")

    # Invalid email format error from Supabase
    msg_bad_email = supabase_auth._parse_supabase_error(
        400,
        {"code": 400, "error_code": "validation_failed", "msg": "Invalid email"},
        "Default"
    )
    assert "format" in msg_bad_email.lower(), f"Expected email format alert, got: {msg_bad_email}"
    print(f"[PASS] Raw 'Invalid email' translated into helpful format guidance")

    # 4. TEST LOCAL SIGNUP & SIGNIN FLOW
    print("\n[TEST 4] Testing Local Auth Multi-User Flow")
    email_test = f"test_{uuid.uuid4().hex[:6]}@domain.com"
    pw_test = "SecurePass123"

    ok_up, msg_up, user_up = supabase_auth._local_sign_up(email_test, pw_test)
    assert ok_up, f"Local signup failed: {msg_up}"
    assert user_up and "id" in user_up
    print(f"[PASS] Local signup succeeded for {email_test}")

    # Duplicate should fail with clear message
    ok_dup, msg_dup_local, _ = supabase_auth._local_sign_up(email_test, pw_test)
    assert not ok_dup
    assert ("already registered" in msg_dup_local.lower() or "already exists" in msg_dup_local.lower())
    print(f"[PASS] Duplicate signup blocked: {msg_dup_local}")

    # Signin with right credentials
    ok_in, msg_in, user_in = supabase_auth._local_sign_in(email_test, pw_test)
    assert ok_in and user_in["id"] == user_up["id"]
    print(f"[PASS] Local signin succeeded: {msg_in}")

    # Signin with wrong password
    ok_bad_pw, msg_bad_pw, _ = supabase_auth._local_sign_in(email_test, "WrongPassword")
    assert not ok_bad_pw
    print(f"[PASS] Wrong password rejected: {msg_bad_pw}")

    # Signin with uppercase version should succeed due to normalization
    ok_upper, _, _ = supabase_auth._local_sign_in(email_test.upper(), pw_test)
    assert ok_upper, "Uppercase email should match after normalization"
    print(f"[PASS] Uppercase email normalization verified on signin")

    # 5. TEST INVALID INPUT REJECTION BEFORE NETWORK CALL
    print("\n[TEST 5] Testing Pre-flight Validation (No network waste)")
    ok_inv, msg_inv, _ = supabase_auth.sign_in("notanemail", "password")
    assert not ok_inv
    assert "valid email" in msg_inv.lower()
    print(f"[PASS] Malformed email rejected before sending: {msg_inv}")

    ok_short, msg_short, _ = supabase_auth.sign_up("valid@domain.com", "123")
    assert not ok_short
    assert "6 characters" in msg_short
    print(f"[PASS] Short password rejected before sending: {msg_short}")

    print("\n==================================================")
    print("ALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_auth_suite()

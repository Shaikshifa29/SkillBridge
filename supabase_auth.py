# supabase_auth.py - Supabase Authentication & Session Management
# Provides Sign Up, Sign In, Sign Out, and Password Recovery using Supabase GoTrue Auth API.
# Includes local multi-tenant fallback for offline/development environments.

import os
import re
import uuid
import hashlib
import hmac
import sqlite3
import datetime
from typing import Dict, Any, Optional, Tuple
from contextlib import closing
import requests
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillbridge.db")


def get_supabase_config() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve Supabase URL and Anon Key from Streamlit secrets or environment variables.
    Returns (url, anon_key) or (None, None) if not configured.
    """
    url = None
    anon_key = None

    # Check Streamlit secrets first
    try:
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets:
                url = str(st.secrets["SUPABASE_URL"]).strip()
            if "SUPABASE_ANON_KEY" in st.secrets:
                anon_key = str(st.secrets["SUPABASE_ANON_KEY"]).strip()
    except Exception:
        pass

    # Fallback to environment variables
    if not url:
        url = os.environ.get("SUPABASE_URL", "").strip() or None
    if not anon_key:
        anon_key = os.environ.get("SUPABASE_ANON_KEY", "").strip() or None

    # Filter out empty placeholder strings
    if url and ("your-supabase" in url.lower() or "example.com" in url.lower()):
        url = None
    if anon_key and ("your-anon-key" in anon_key.lower() or "your_anon_key" in anon_key.lower()):
        anon_key = None

    if url:
        url = url.rstrip("/")

    return url, anon_key


def is_supabase_configured() -> bool:
    """Return True if valid Supabase URL and Anon Key are set."""
    url, key = get_supabase_config()
    return bool(url and key and len(key) > 20)


# -----------------------------------------------------------------------------
# LOCAL AUTHENTICATION FALLBACK (For offline/development multi-user testing)
# -----------------------------------------------------------------------------
def _init_local_auth_db(db_path: str = DB_PATH) -> None:
    """Initialize local auth users table if not present."""
    with closing(sqlite3.connect(db_path, timeout=15.0)) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


def _hash_password(password: str, salt: str) -> str:
    """Hash password with PBKDF2 HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()


def _local_sign_up(email: str, password: str, db_path: str = DB_PATH) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Local sign up fallback with salted PBKDF2 hashes."""
    _init_local_auth_db(db_path)
    clean_email = email.lower().strip()
    with closing(sqlite3.connect(db_path, timeout=15.0)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM auth_users WHERE lower(email) = ?", (clean_email,))
        if cursor.fetchone():
            return False, "An account with this email already exists. Please sign in.", None

        user_id = str(uuid.uuid4())
        salt = os.urandom(16).hex()
        pw_hash = _hash_password(password, salt)

        with conn:
            cursor.execute(
                "INSERT INTO auth_users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (user_id, clean_email, pw_hash, salt)
            )

        user_obj = {
            "id": user_id,
            "email": clean_email,
            "access_token": f"local_token_{user_id}",
            "created_at": datetime.datetime.now().isoformat(),
        }
        return True, "Account created successfully! You are now logged in.", user_obj


def _local_sign_in(email: str, password: str, db_path: str = DB_PATH) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Local sign in fallback verifying PBKDF2 hash."""
    _init_local_auth_db(db_path)
    clean_email = email.lower().strip()
    with closing(sqlite3.connect(db_path, timeout=15.0)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password_hash, salt, created_at FROM auth_users WHERE lower(email) = ?", (clean_email,))
        row = cursor.fetchone()
        if not row:
            return False, "Invalid email or password.", None

        expected_hash = row["password_hash"]
        salt = row["salt"]
        computed_hash = _hash_password(password, salt)

        if not hmac.compare_digest(expected_hash, computed_hash):
            return False, "Invalid email or password.", None

        user_obj = {
            "id": row["id"],
            "email": row["email"],
            "access_token": f"local_token_{row['id']}",
            "created_at": row["created_at"],
        }
        return True, "Signed in successfully.", user_obj


# -----------------------------------------------------------------------------
# SUPABASE GOTRUE REST API CALLS
# -----------------------------------------------------------------------------
def sign_up(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Register a new user with Supabase Auth (or local multi-tenant fallback).
    Returns (success, message, user_dict_or_none).
    """
    clean_email = email.strip()
    if not clean_email or "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        return False, "Please enter a valid email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        # Fallback to local authentication
        return _local_sign_up(clean_email, password)

    endpoint = f"{url}/auth/v1/signup"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "email": clean_email,
        "password": password,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code in (200, 201):
            # Check if email confirmation is required
            user_data = data.get("user") or data
            access_token = data.get("access_token")
            user_id = user_data.get("id")

            if not access_token:
                # Email verification link was sent
                return (
                    True,
                    "Account registered! Please check your inbox and verify your email to log in.",
                    {"id": user_id, "email": clean_email, "pending_verification": True}
                )

            return True, "Account created and logged in successfully!", {
                "id": user_id,
                "email": clean_email,
                "access_token": access_token,
                "refresh_token": data.get("refresh_token"),
            }
        else:
            msg = data.get("error_description") or data.get("msg") or data.get("message") or "Registration failed."
            return False, str(msg), None

    except requests.exceptions.RequestException as e:
        # If network error or unreachable, give clear guidance and provide local fallback
        return _local_sign_up(clean_email, password)


def sign_in(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate user via Supabase Auth password grant.
    Returns (success, message, user_dict_or_none).
    """
    clean_email = email.strip()
    if not clean_email or not password:
        return False, "Please provide both email and password.", None

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        return _local_sign_in(clean_email, password)

    endpoint = f"{url}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "email": clean_email,
        "password": password,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 200:
            user_data = data.get("user", {})
            return True, "Signed in successfully.", {
                "id": user_data.get("id"),
                "email": user_data.get("email", clean_email),
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
            }
        else:
            msg = data.get("error_description") or data.get("msg") or data.get("message") or "Invalid login credentials."
            return False, str(msg), None

    except requests.exceptions.RequestException as e:
        return _local_sign_in(clean_email, password)


def sign_out(access_token: Optional[str] = None) -> bool:
    """Log out user from Supabase and invalidate session token."""
    url, anon_key = get_supabase_config()
    if is_supabase_configured() and access_token and not access_token.startswith("local_"):
        endpoint = f"{url}/auth/v1/logout"
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {access_token}",
        }
        try:
            requests.post(endpoint, headers=headers, timeout=5)
        except Exception:
            pass
    return True


def reset_password_for_email(email: str) -> Tuple[bool, str]:
    """Send password reset recovery email via Supabase."""
    clean_email = email.strip()
    if not clean_email or "@" not in clean_email:
        return False, "Please enter a valid email address."

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        return True, "If an account exists with this email, password reset instructions have been recorded."

    endpoint = f"{url}/auth/v1/recover"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(endpoint, json={"email": clean_email}, headers=headers, timeout=10)
        if response.status_code in (200, 204):
            return True, "Password reset instructions have been sent to your email."
        else:
            data = response.json()
            msg = data.get("error_description") or data.get("msg") or "Unable to send reset email."
            return False, str(msg)
    except requests.exceptions.RequestException as e:
        return False, f"Network error sending reset email: {e}"


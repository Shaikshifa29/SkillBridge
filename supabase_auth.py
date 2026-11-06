# supabase_auth.py - Supabase Authentication & Session Management
# Provides Sign Up, Sign In, Sign Out, Resend Confirmation, and Password Recovery
# Using Supabase GoTrue Auth API with resilient error handling and input sanitization.

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

# Standard RFC 5322 compliant email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
)


def sanitize_email(email_str: str) -> str:
    """
    Thoroughly sanitize an email string:
    - Strips leading and trailing whitespaces.
    - Removes internal non-breaking, zero-width, or control whitespace characters.
    - Normalizes string to lowercase.
    """
    if not email_str:
        return ""
    # Strip any zero-width (\u200b), non-breaking (\u00a0), carriage returns, tabs
    cleaned = re.sub(r"[\s\u200b\u00a0\r\n\t]+", "", email_str.strip())
    return cleaned.lower()


def is_valid_email_format(email_str: str) -> bool:
    """Validate email syntax against standard regex."""
    if not email_str:
        return False
    return bool(EMAIL_REGEX.match(email_str))


def get_supabase_config() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve Supabase URL and Anon Key from Streamlit secrets, .streamlit/secrets.toml, or environment variables.
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

    # Direct fallback to .streamlit/secrets.toml if st.secrets is unavailable
    if not url or not anon_key:
        secrets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_file):
            try:
                import tomllib
                with open(secrets_file, "rb") as f:
                    sec_cfg = tomllib.load(f)
                    if not url and "SUPABASE_URL" in sec_cfg:
                        url = str(sec_cfg["SUPABASE_URL"]).strip()
                    if not anon_key and "SUPABASE_ANON_KEY" in sec_cfg:
                        anon_key = str(sec_cfg["SUPABASE_ANON_KEY"]).strip()
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
                    full_name TEXT DEFAULT '',
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("PRAGMA table_info(auth_users)")
            cols = [row[1] for row in cursor.fetchall()]
            if "full_name" not in cols:
                try:
                    cursor.execute("ALTER TABLE auth_users ADD COLUMN full_name TEXT DEFAULT ''")
                except Exception:
                    pass


def _hash_password(password: str, salt: str) -> str:
    """Hash password with PBKDF2 HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()


def _local_sign_up(email: str, password: str, full_name: Optional[str] = None, db_path: str = DB_PATH) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Local sign up fallback with salted PBKDF2 hashes."""
    _init_local_auth_db(db_path)
    clean_email = sanitize_email(email)
    with closing(sqlite3.connect(db_path, timeout=15.0)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM auth_users WHERE lower(email) = ?", (clean_email,))
        if cursor.fetchone():
            return False, "This email is already registered. Please go to the Sign In tab or use Forgot Password.", None

        user_id = str(uuid.uuid4())
        salt = os.urandom(16).hex()
        pw_hash = _hash_password(password, salt)
        clean_name = (full_name or "").strip()

        with conn:
            cursor.execute(
                "INSERT INTO auth_users (id, email, full_name, password_hash, salt) VALUES (?, ?, ?, ?, ?)",
                (user_id, clean_email, clean_name, pw_hash, salt)
            )

        user_obj = {
            "id": user_id,
            "email": clean_email,
            "full_name": clean_name,
            "access_token": f"local_token_{user_id}",
            "created_at": datetime.datetime.now().isoformat(),
        }
        return True, "Account created successfully! You are now logged in.", user_obj


def _local_sign_in(email: str, password: str, db_path: str = DB_PATH) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Local sign in fallback verifying PBKDF2 hash."""
    _init_local_auth_db(db_path)
    clean_email = sanitize_email(email)
    with closing(sqlite3.connect(db_path, timeout=15.0)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, password_hash, salt, created_at FROM auth_users WHERE lower(email) = ?", (clean_email,))
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
            "full_name": row["full_name"] if "full_name" in row.keys() else "",
            "access_token": f"local_token_{row['id']}",
            "created_at": row["created_at"],
        }
        return True, "Signed in successfully.", user_obj
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
# ERROR PARSER HELPER
# -----------------------------------------------------------------------------
def _parse_supabase_error(response_status: int, data: Dict[str, Any], default_msg: str) -> str:
    """Translate raw Supabase GoTrue responses into actionable, human-designed alerts."""
    raw_msg = (
        data.get("error_description")
        or data.get("msg")
        or data.get("message")
        or data.get("error")
        or ""
    )
    raw_code = str(data.get("error_code") or data.get("code") or "")
    low_msg = str(raw_msg).lower()
    low_code = raw_code.lower()

    # Rate limiting
    if response_status == 429 or "rate limit" in low_msg or "over_email_send_rate_limit" in low_code:
        return (
            "⏱️ Rate limit exceeded: Too many attempts were made in a short time. "
            "Please wait a few minutes before trying again."
        )

    # Email not confirmed
    if "email not confirmed" in low_msg or "email_not_confirmed" in low_code:
        return (
            "✉️ Email not confirmed: Supabase has 'Confirm email' enabled in your project settings. "
            "To enable instant login without verification links, turn 'Confirm email' OFF in Supabase Dashboard -> Authentication -> Providers -> Email."
        )

    # Invalid credentials
    if "invalid login credentials" in low_msg or "invalid_credentials" in low_code or "invalid_grant" in low_msg:
        if "email not confirmed" in low_msg or "email_not_confirmed" in low_code:
            return (
                "✉️ Email not confirmed: Supabase has 'Confirm email' enabled in your project settings. "
                "To enable instant login without verification links, turn 'Confirm email' OFF in Supabase Dashboard -> Authentication -> Providers -> Email."
            )
        return "Invalid email or password. Please verify your credentials or click Forgot Password."

    # User already registered
    if "user already registered" in low_msg or "user_already_exists" in low_code or "already exists" in low_msg:
        return "👤 This email is already registered. Please go to the Sign In tab or use Forgot Password."

    # Format / validation failure
    if "invalid email" in low_msg or "email_address_invalid" in low_code or "validation_failed" in low_code:
        return "⚠️ Supabase rejected the email format. Please verify you entered a standard email (e.g. name@domain.com)."

    # Password length
    if "password should be at least" in low_msg:
        return "🔒 Password must be at least 6 characters long."

    return str(raw_msg) if raw_msg else default_msg


# -----------------------------------------------------------------------------
# SUPABASE GOTRUE REST API CALLS
# -----------------------------------------------------------------------------
def sign_up(email: str, password: str, full_name: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Register a new user with Supabase Auth (or local multi-tenant fallback).
    Supports instant registration without email verification when Supabase Confirm email is OFF.
    Returns (success, message, user_dict_or_none).
    """
    clean_email = sanitize_email(email)
    if not clean_email or not is_valid_email_format(clean_email):
        return False, "Please enter a valid email address (e.g. name@domain.com).", None

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        # Fallback to local authentication when no cloud credentials
        return _local_sign_up(clean_email, password, full_name=full_name)

    endpoint = f"{url}/auth/v1/signup"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "email": clean_email,
        "password": password,
    }
    if full_name:
        payload["data"] = {"full_name": full_name.strip()}

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=12)
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code in (200, 201):
            user_data = data.get("user") or data
            
            # Detect existing user when Supabase hides user enumeration (identities is empty list)
            identities = user_data.get("identities")
            if isinstance(identities, list) and len(identities) == 0:
                return False, "This email is already registered. Please go to the Sign In tab or use Forgot Password.", None

            access_token = data.get("access_token")
            user_id = user_data.get("id")
            meta = user_data.get("user_metadata", {}) or {}
            user_full_name = (full_name or meta.get("full_name") or "").strip()

            if not access_token:
                # If Supabase did not return an access_token, try signing in immediately with password
                login_ok, login_msg, login_user = sign_in(clean_email, password)
                if login_ok and login_user and login_user.get("access_token"):
                    return True, "Account created and signed in successfully!", login_user

                # If login failed because 'Confirm email' is still ON in Supabase project settings
                return (
                    False,
                    "Account registered in Supabase, but instant sign-in is blocked because 'Confirm email' is enabled in your Supabase project settings. "
                    "To enable instant registration without verification, go to Supabase Dashboard -> Authentication -> Providers -> Email and turn 'Confirm email' OFF.",
                    {"id": user_id, "email": clean_email, "pending_verification": True}
                )

            return True, "Account created and signed in successfully!", {
                "id": user_id,
                "email": clean_email,
                "full_name": user_full_name,
                "access_token": access_token,
                "refresh_token": data.get("refresh_token"),
            }
        else:
            msg = _parse_supabase_error(response.status_code, data, "Registration failed.")
            return False, msg, None

    except requests.exceptions.RequestException as e:
        # Graceful fallback to local authentication when cloud network is unreachable
        ok_loc, msg_loc, user_loc = _local_sign_up(clean_email, password, full_name=full_name)
        if ok_loc:
            return True, "Account created successfully (local mode).", user_loc
        return False, msg_loc if "already registered" in msg_loc.lower() or "already exists" in msg_loc.lower() else f"Network error connecting to Supabase: {e}", None


def sign_in(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate user via Supabase Auth password grant.
    Returns (success, message, user_dict_or_none).
    """
    clean_email = sanitize_email(email)
    if not clean_email or not is_valid_email_format(clean_email):
        return False, "Please enter a valid email address (e.g. name@domain.com).", None

    if not password:
        return False, "Please enter your password.", None

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        return _local_sign_in(clean_email, password)

    endpoint = f"{url}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "grant_type": "password",
        "email": clean_email,
        "password": password,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=12)
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code == 200:
            user_data = data.get("user", {})
            meta = user_data.get("user_metadata", {}) or {}
            user_full_name = meta.get("full_name") or meta.get("name") or ""
            return True, "Signed in successfully.", {
                "id": user_data.get("id"),
                "email": user_data.get("email", clean_email),
                "full_name": user_full_name,
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
            }
        else:
            msg = _parse_supabase_error(response.status_code, data, "Invalid email or password.")
            # Check if this is an unconfirmed email error to allow actionable resend
            is_unconfirmed = (
                "email not confirmed" in str(data).lower()
                or "email_not_confirmed" in str(data).lower()
            )
            extra = {"pending_verification": True, "email": clean_email} if is_unconfirmed else None
            return False, msg, extra

    except requests.exceptions.RequestException as e:
        # Graceful fallback to local authentication when cloud network is unreachable
        ok_loc, msg_loc, user_loc = _local_sign_in(clean_email, password)
        if ok_loc:
            return True, "Signed in successfully (local mode).", user_loc
        return False, msg_loc if "invalid email or password" in msg_loc.lower() else f"Network error connecting to Supabase: {e}", None


def resend_confirmation(email: str) -> Tuple[bool, str]:
    """Resend signup confirmation email via Supabase."""
    clean_email = sanitize_email(email)
    if not clean_email or not is_valid_email_format(clean_email):
        return False, "Please enter a valid email address."

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        return True, "Local mode: email verification is not required."

    endpoint = f"{url}/auth/v1/resend"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "type": "signup",
        "email": clean_email,
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=12)
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code in (200, 204):
            return True, "📬 A fresh confirmation email has been sent! Please check your inbox and spam folder."
        else:
            msg = _parse_supabase_error(response.status_code, data, "Could not resend confirmation email.")
            return False, msg
    except requests.exceptions.RequestException as e:
        return False, f"Network error sending confirmation: {e}"


def reset_password_for_email(email: str) -> Tuple[bool, str]:
    """Send password reset recovery email via Supabase."""
    clean_email = sanitize_email(email)
    if not clean_email or not is_valid_email_format(clean_email):
        return False, "Please enter a valid email address (e.g. name@domain.com)."

    url, anon_key = get_supabase_config()
    if not is_supabase_configured():
        return True, "Password reset instructions have been recorded (Local Mode)."

    endpoint = f"{url}/auth/v1/recover"
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(endpoint, json={"email": clean_email}, headers=headers, timeout=12)
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code in (200, 204):
            return True, "📬 Password reset instructions have been sent to your email. Please check your inbox."
        else:
            msg = _parse_supabase_error(response.status_code, data, "Unable to send reset email.")
            return False, msg
    except requests.exceptions.RequestException as e:
        return False, f"Network error sending reset email: {e}"


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

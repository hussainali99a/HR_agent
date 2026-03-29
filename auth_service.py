import hashlib
import uuid
from datetime import datetime, timedelta

from database import db
from email_sender import email_sender

# =========================
# PASSWORD HASHING
# =========================
def hash_password(password: str) -> str:
    """Hash password securely"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# =========================
# SIGNUP
# =========================
def signup_user(name:str, company:str, email: str, password: str):
    """Create user + generate verification token"""

    existing = db.get_user(email)
    if existing:
        return {"success": False, "message": "User already exists"}

    hashed = hash_password(password)

    user_id = db.create_user(name, company, email, hashed)

    token = generate_verification_token(user_id)

    email_sender.send_verification_email(email, name, f"http://localhost:8501/verify?u={user_id}&token={token}")


    return {
        "success": True,
        "user_id": user_id,
    }


# =========================
# VERIFICATION
# =========================
def generate_verification_token(user_id: int):
    token = str(uuid.uuid4())

    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO verification_tokens (user_id, token, created_at)
        VALUES (?, ?, ?)
    """, (user_id, token, datetime.now()))

    conn.commit()
    conn.close()

    return token


def verify_user_token(user_id: int, token: str):
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id FROM verification_tokens WHERE user_id=? AND token=?
    """, (user_id, token))

    result = cur.fetchone()

    if not result:
        return {"success": False, "message": "Invalid token"}

    user_id = result[0]

    # mark verified
    db.verify_user(user_id)

    # delete token (optional)
    cur.execute("DELETE FROM verification_tokens WHERE token=?", (token,))
    conn.commit()
    conn.close()

    return {"success": True, "user_id": user_id}


# =========================
# LOGIN
# =========================
def login_user(email: str, password: str):
    user = db.get_user(email)

    if not user:
        return {"success": False, "message": "User not found"}

    user_id = user[0]
    stored_email = user[3]
    stored_password = user[4]
    is_verified = user[5]

    if not verify_password(password, stored_password):
        return {"success": False, "message": "Incorrect password"}

    if not is_verified:
        return {"success": False, "message": "Email not verified"}

    return {
        "success": True,
        "user_id": user_id,
        "email": stored_email
    }


# =========================
# SESSION HELPERS
# =========================
def logout_user():
    return {"success": True}


def get_current_user(session_state):
    """Streamlit session helper"""
    return session_state.get("user_id", None)
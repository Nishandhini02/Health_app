

# auth.py
import re
import sqlite3

try:
    import bcrypt
    _BCRYPT = True
except ImportError:
    _BCRYPT = False          # fallback: plain-text compare (dev only)

from database import get_connection, create_tables, log_activity

create_tables()

# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
def _validate_password(password: str):
    """Returns (ok: bool, message: str)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "Password must contain at least one special character."
    return True, "OK"


def _hash(password: str) -> str:
    if _BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return password                         # plain-text fallback


def _verify(password: str, stored: str) -> bool:
    if _BCRYPT:
        try:
            return bcrypt.checkpw(password.encode(), stored.encode())
        except Exception:
            return password == stored       # old plain-text rows
    return password == stored


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def register_user(username: str, password: str):
    if not username.strip():
        return False, "Username cannot be empty."

    ok, msg = _validate_password(password)
    if not ok:
        return False, msg

    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username.strip(), _hash(password), "user")
        )
        conn.commit()
        conn.close()
        log_activity(username, "Registered")
        return True, "Registered successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, str(e)


def login_user(username: str, password: str) -> bool:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username.strip(),))
        row = c.fetchone()
        conn.close()
        if row and _verify(password, row[0]):
            log_activity(username, "Login")
            return True
        return False
    except Exception:
        return False


def get_role(username: str) -> str:
    from database import get_user_role
    return get_user_role(username)
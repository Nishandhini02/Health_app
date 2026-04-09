# import sqlite3

# def get_connection():
#     return sqlite3.connect("mediai.db", check_same_thread=False)

# def create_tables():
#     conn = get_connection()
#     c = conn.cursor()

#     # Users
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE,
#         password TEXT
#     )
#     """)

#     # Chats
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS chats (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT,
#         title TEXT
#     )
#     """)

#     # Messages
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS messages (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         chat_id INTEGER,
#         role TEXT,
#         message TEXT
#     )
#     """)

#     conn.commit()
#     conn.close()


# # database.py
# import sqlite3

# def get_connection():
#     return sqlite3.connect("mediai.db", check_same_thread=False)

# def create_tables():
#     conn = get_connection()
#     c = conn.cursor()

#     # Users — role column added (default "user", admin = "admin")
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id       INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE,
#         password TEXT,
#         role     TEXT DEFAULT 'user'
#     )
#     """)

#     # Add role column if upgrading from old DB (safe no-op if already exists)
#     try:
#         c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
#     except Exception:
#         pass

#     # Ensure a default admin account exists (change password before production!)
#     c.execute("SELECT * FROM users WHERE username='admin'")
#     if not c.fetchone():
#         c.execute(
#             "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
#             ("admin", "Admin@123", "admin")
#         )

#     # Chats
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS chats (
#         id       INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT,
#         title    TEXT
#     )
#     """)

#     # Messages
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS messages (
#         id      INTEGER PRIMARY KEY AUTOINCREMENT,
#         chat_id INTEGER,
#         role    TEXT,
#         message TEXT
#     )
#     """)

#     # Activity log — tracks key user actions for admin dashboard
#     c.execute("""
#     CREATE TABLE IF NOT EXISTS activity_log (
#         id        INTEGER PRIMARY KEY AUTOINCREMENT,
#         username  TEXT,
#         action    TEXT,
#         detail    TEXT,
#         timestamp TEXT DEFAULT (datetime('now','localtime'))
#     )
#     """)

#     conn.commit()
#     conn.close()


# def log_activity(username: str, action: str, detail: str = ""):
#     """Call this wherever you want to track user actions."""
#     try:
#         conn = get_connection()
#         c = conn.cursor()
#         c.execute(
#             "INSERT INTO activity_log (username, action, detail) VALUES (?, ?, ?)",
#             (username, action, detail)
#         )
#         conn.commit()
#         conn.close()
#     except Exception:
#         pass


# def get_user_role(username: str) -> str:
#     """Returns 'admin' or 'user'."""
#     try:
#         conn = get_connection()
#         c = conn.cursor()
#         c.execute("SELECT role FROM users WHERE username=?", (username,))
#         row = c.fetchone()
#         conn.close()
#         return row[0] if row and row[0] else "user"
#     except Exception:
#         return "user"---new one morning came 1.04


# database.py
import os
import sqlite3


def get_connection():
    return sqlite3.connect("mediai.db", check_same_thread=False)


def _hash_password(password: str) -> str:
    """Hash with bcrypt. Falls back to plain text if bcrypt not installed."""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        return password


def create_tables():
    conn = get_connection()
    c = conn.cursor()

    # ── Users table ───────────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role     TEXT DEFAULT 'user'
    )
    """)

    # Safe upgrade for older DBs that don't have the role column yet
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except Exception:
        pass

    # ── Admin account setup ───────────────────────────────────────────────
    #
    #  HOW THE ADMIN PASSWORD WORKS
    #  ─────────────────────────────
    #  The admin password is read from an ENVIRONMENT VARIABLE called
    #  MEDIAI_ADMIN_PASSWORD so it is NEVER written in this source file.
    #
    #  STEP 1 — Set the environment variable BEFORE running the app:
    #
    #    Windows (Command Prompt):
    #      set MEDIAI_ADMIN_PASSWORD=MySecurePass@99
    #      streamlit run app.py
    #
    #    Windows (PowerShell):
    #      $env:MEDIAI_ADMIN_PASSWORD="MySecurePass@99"
    #      streamlit run app.py
    #
    #    Mac / Linux:
    #      export MEDIAI_ADMIN_PASSWORD=MySecurePass@99
    #      streamlit run app.py
    #
    #  STEP 2 — Log in to the app:
    #      Username : admin
    #      Password : whatever you set in MEDIAI_ADMIN_PASSWORD
    #
    #  WHAT HAPPENS IF YOU DON'T SET THE ENV VAR?
    #  ────────────────────────────────────────────
    #  A strong random 16-character password is auto-generated and
    #  PRINTED TO THE TERMINAL once so you can copy it and log in.
    #  Example terminal output:
    #
    #    ============================================================
    #      ⚠️  MEDIAI_ADMIN_PASSWORD is not set.
    #      Auto-generated admin password: aB3$kR9!mZ2@xQ7w
    #      Copy the password above and log in as admin.
    #      Set MEDIAI_ADMIN_PASSWORD to use a fixed password.
    #    ============================================================
    #
    #  The password is stored HASHED (bcrypt) in the database —
    #  never in plain text. Even if someone reads mediai.db they
    #  cannot recover the original password.
    #
    #  IMPORTANT: The password is only written on the VERY FIRST RUN
    #  (when the admin row does not exist yet). After that, the env
    #  var is ignored — so changing MEDIAI_ADMIN_PASSWORD later will
    #  NOT change the stored password. Use the Admin Panel inside the
    #  app to change it after first login.
    # ─────────────────────────────────────────────────────────────────────

    c.execute("SELECT id FROM users WHERE username='admin1'")
    admin_exists = c.fetchone()

    if not admin_exists:
        # First run — create the admin account
        admin_password = os.environ.get("MEDIAI_ADMIN_PASSWORD", "").strip()

        if not admin_password:
            # No env var set — generate a secure random password and print it
            import secrets, string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            admin_password = "".join(secrets.choice(alphabet) for _ in range(16))
            print("\n" + "=" * 60)
            print("  ⚠️  MEDIAI_ADMIN_PASSWORD is not set.")
            print(f"  Auto-generated admin password: {admin_password}")
            print("  Copy the password above and log in as admin.")
            print("  Set MEDIAI_ADMIN_PASSWORD to use a fixed password.")
            print("=" * 60 + "\n")
        else:
            print(f"\n✅ Admin account created using MEDIAI_ADMIN_PASSWORD.\n")

        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin1", _hash_password(admin_password), "admin")
        )

    # ── Other tables ──────────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title    TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role    TEXT,
        message TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username  TEXT,
        action    TEXT,
        detail    TEXT,
        timestamp TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    conn.commit()
    conn.close()


def log_activity(username: str, action: str, detail: str = ""):
    """Record a user action in the activity log (used by admin dashboard)."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO activity_log (username, action, detail) VALUES (?, ?, ?)",
            (username, action, detail)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_user_role(username: str) -> str:
    """Returns 'admin' or 'user'."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        return row[0] if row and row[0] else "user"
    except Exception:
        return "user"
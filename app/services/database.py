import sqlite3

from app.config import DB_NAME


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_secret TEXT NOT NULL,
            chat_id TEXT,
            pin_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "pin_hash" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN pin_hash TEXT")
    conn.commit()
    conn.close()


def save_user(phone, password_hash, totp_secret, chat_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (phone, password_hash, totp_secret, chat_id) VALUES (?, ?, ?, ?)",
        (phone, password_hash, totp_secret, chat_id),
    )
    conn.commit()
    conn.close()


def get_user_by_phone(phone):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def update_user_pin(phone, pin_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET pin_hash = ? WHERE phone = ?", (pin_hash, phone))
    conn.commit()
    conn.close()


def update_user_password(phone, password_hash):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE phone = ?", (password_hash, phone))
    conn.commit()
    conn.close()

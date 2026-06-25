# db.py
import sqlite3

DB_PATH = "bot.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def set_premium(user_id: int, value: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            premium INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        INSERT INTO users (user_id, premium)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET premium=excluded.premium
    """, (user_id, value))

    conn.commit()
    conn.close()


def is_premium(user_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT premium FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()

    return bool(row and row[0] == 1)
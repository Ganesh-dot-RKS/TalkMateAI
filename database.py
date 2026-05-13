# database.py
import sqlite3
from datetime import datetime

DB_NAME = "talkmate.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grammar_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_user_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_result(original, corrected, user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO grammar_history (user_text, corrected_text, user_id) VALUES (?, ?, ?)",
        (original, corrected, user_id)
    )
    conn.commit()
    conn.close()
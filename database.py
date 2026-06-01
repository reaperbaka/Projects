# ── database.py ──────────────────────────────────────────────────────────────
import sqlite3
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "library.db")
    return "library.db"

conn = sqlite3.connect(get_db_path())
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    password   TEXT NOT NULL,
    class      TEXT NOT NULL,
    year       TEXT NOT NULL,
    phone      STRING NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS book (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    author           TEXT NOT NULL,
    total_copies     INTEGER NOT NULL,
    available_copies INTEGER NOT NULL,
    publication      TEXT NOT NULL,
    price            INTEGER NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS issued (
    issue_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_id   TEXT NOT NULL,
    book_id      INTEGER NOT NULL,
    issue_date   TEXT NOT NULL,
    due_date     TEXT NOT NULL,
    return_date  TEXT,
    fine         INTEGER DEFAULT 0,
    FOREIGN KEY(book_id) REFERENCES book(book_id)
)""")

cursor.execute(
    "INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)",
    ("admin", "admin123")
)
conn.commit()
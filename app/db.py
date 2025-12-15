import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS onboarding_requests (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            employee_name TEXT NOT NULL,
            manager_name TEXT NOT NULL,
            role TEXT NOT NULL,
            grade TEXT NOT NULL,
            start_date TEXT NOT NULL,
            status TEXT NOT NULL,
            rejection_reason TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            onboarding_id TEXT NOT NULL,
            owner TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            due_date TEXT NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0,
            last_reminded_at TEXT,
            FOREIGN KEY (onboarding_id) REFERENCES onboarding_requests(id)
        )
        """
    )
    conn.commit()
    conn.close()

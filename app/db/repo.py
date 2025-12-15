from __future__ import annotations
from typing import Optional, List, Dict, Any
import uuid

from app.db import get_conn
from app.utils.time import now_jst

def create_onboarding(employee_name: str, manager_name: str, role: str, grade: str, start_date: str) -> str:
    oid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        """INSERT INTO onboarding_requests
           (id, created_at, employee_name, manager_name, role, grade, start_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (oid, now_jst().isoformat(), employee_name, manager_name, role, grade, start_date, "PENDING"),
    )
    conn.commit()
    conn.close()
    return oid

def get_onboarding(oid: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM onboarding_requests WHERE id = ?", (oid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def list_onboardings() -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM onboarding_requests ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_status(oid: str, status: str, rejection_reason: Optional[str] = None) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE onboarding_requests SET status = ?, rejection_reason = ? WHERE id = ?",
        (status, rejection_reason, oid),
    )
    conn.commit()
    conn.close()

def add_task(onboarding_id: str, owner: str, title: str, description: str, due_date: str) -> None:
    tid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        """INSERT INTO tasks (id, onboarding_id, owner, title, description, due_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (tid, onboarding_id, owner, title, description, due_date),
    )
    conn.commit()
    conn.close()

def list_tasks(onboarding_id: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE onboarding_id = ? ORDER BY due_date ASC",
        (onboarding_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_done(task_id: str, done: bool) -> None:
    conn = get_conn()
    conn.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (1 if done else 0, task_id))
    conn.commit()
    conn.close()

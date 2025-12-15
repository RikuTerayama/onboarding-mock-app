from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import init_db, get_conn
from app.db.repo import (
    create_onboarding, get_onboarding, list_onboardings, set_status,
    add_task, list_tasks, mark_done
)
from app.services.template_engine import generate
from app.utils.time import now_jst, parse_date

app = FastAPI(title="Onboarding Mock App", version="0.1.0")
templates = Jinja2Templates(directory=str((__import__("pathlib").Path(__file__).parent / "templates")))

@app.on_event("startup")
def _startup() -> None:
    init_db()

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    onboardings = list_onboardings()
    return templates.TemplateResponse("home.html", {"request": request, "onboardings": onboardings})

@app.get("/onboard", response_class=HTMLResponse)
def onboard_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/onboard")
def onboard_create(
    employee_name: str = Form(...),
    manager_name: str = Form(...),
    role: str = Form(...),
    grade: str = Form(...),
    start_date: str = Form(...),
):
    oid = create_onboarding(employee_name, manager_name, role, grade, start_date)
    return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

@app.get("/onboarding/{oid}", response_class=HTMLResponse)
def onboarding_detail(request: Request, oid: str):
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)

    # For exec demo: show which template would be used
    start = parse_date(onboarding["start_date"])
    _, plan, template_used = generate(onboarding["role"], onboarding["grade"], start)

    tasks = list_tasks(oid)

    class Obj:
        def __init__(self, d): self.__dict__.update(d)

    plan_obj = Obj({"employee": Obj(plan["employee"]), "manager": Obj(plan["manager"])})

    return templates.TemplateResponse(
        "detail.html",
        {"request": request, "onboarding": onboarding, "tasks": tasks, "plan": plan_obj, "template_used": template_used},
    )

@app.post("/onboarding/{oid}/approve")
def approve(oid: str):
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)

    if onboarding["status"] != "PENDING":
        return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

    set_status(oid, "APPROVED", None)

    start = parse_date(onboarding["start_date"])
    tasks_gen, _, _ = generate(onboarding["role"], onboarding["grade"], start)

    for t in tasks_gen:
        owner = onboarding["employee_name"] if t.owner == "employee" else onboarding["manager_name"] if t.owner == "manager" else "HR"
        add_task(oid, owner, t.title, t.description, t.due_date.isoformat())

    return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

@app.get("/onboarding/{oid}/reject", response_class=HTMLResponse)
def reject_form(request: Request, oid: str):
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse("reject.html", {"request": request, "onboarding": onboarding})

@app.post("/onboarding/{oid}/reject")
def reject_submit(oid: str, reason: str = Form(...)):
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)
    set_status(oid, "REJECTED", reason)
    return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: str, redirect_to: str = Form("/")):
    conn = get_conn()
    row = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        return RedirectResponse(url=redirect_to, status_code=303)
    mark_done(task_id, not bool(row["is_done"]))
    return RedirectResponse(url=redirect_to, status_code=303)

@app.get("/reminders", response_class=HTMLResponse)
def reminders(request: Request):
    conn = get_conn()
    today = now_jst().date()
    start = (today - timedelta(days=1)).isoformat()
    end = (today + timedelta(days=7)).isoformat()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date BETWEEN ? AND ? ORDER BY due_date ASC",
        (start, end),
    ).fetchall()
    conn.close()
    tasks = [dict(r) for r in rows]
    return templates.TemplateResponse("reminders.html", {"request": request, "tasks": tasks, "messages": []})

@app.post("/reminders/run", response_class=HTMLResponse)
def reminders_run(request: Request):
    conn = get_conn()
    today = now_jst().date()
    targets = [(today + timedelta(days=d)).isoformat() for d in (7, 3, 0)]
    rows = conn.execute(
        f"SELECT * FROM tasks WHERE is_done = 0 AND due_date IN ({','.join('?' for _ in targets)})",
        targets,
    ).fetchall()

    messages: List[Dict[str, Any]] = []
    ts = now_jst().isoformat()

    for r in rows:
        if r["last_reminded_at"] and r["last_reminded_at"][:10] == today.isoformat():
            continue
        messages.append({"to": r["owner"], "title": f"Reminder: {r['title']}", "body": f"Due: {r['due_date']} — {r['description']}"})
        conn.execute("UPDATE tasks SET last_reminded_at = ? WHERE id = ?", (ts, r["id"]))

    conn.commit()
    conn.close()

    # refresh list
    conn = get_conn()
    start = (today - timedelta(days=1)).isoformat()
    end = (today + timedelta(days=7)).isoformat()
    rows2 = conn.execute(
        "SELECT * FROM tasks WHERE due_date BETWEEN ? AND ? ORDER BY due_date ASC",
        (start, end),
    ).fetchall()
    conn.close()
    tasks = [dict(r) for r in rows2]

    return templates.TemplateResponse("reminders.html", {"request": request, "tasks": tasks, "messages": messages})

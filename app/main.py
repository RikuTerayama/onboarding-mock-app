from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import init_db, get_conn
from app.db.repo import (
    create_onboarding, get_onboarding, list_onboardings, set_status,
    add_task, list_tasks, mark_done,
    create_ticket, list_tickets, close_ticket
)
from app.services.template_engine import generate
from app.services.qa_engine import process_question
from app.chat.blocks import create_user_message, create_bot_response
from app.utils.time import now_jst, parse_date
from app.i18n import t

# Slack Bolt統合（オプション）
try:
    from app.slack.bolt_app import handler
    SLACK_ENABLED = handler is not None
except ImportError:
    SLACK_ENABLED = False
    handler = None

app = FastAPI(title="Onboarding Mock App", version="0.1.0")
templates = Jinja2Templates(directory=str((__import__("pathlib").Path(__file__).parent / "templates")))

# Inject t function into templates
templates.env.globals["t"] = t

def get_lang(request: Request) -> str:
    """Determine language: query param > cookie > default 'en'"""
    # Check query parameter first
    lang_query = request.query_params.get("lang", "").lower()
    if lang_query in ("en", "ja"):
        return lang_query
    
    # Check cookie
    lang_cookie = request.cookies.get("lang", "").lower()
    if lang_cookie in ("en", "ja"):
        return lang_cookie
    
    # Default
    return "en"

@app.on_event("startup")
def _startup() -> None:
    init_db()

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/set-lang")
def set_lang(request: Request, lang: str = Query(...), next: str = Query("/")):
    """Set language cookie and redirect"""
    if lang not in ("en", "ja"):
        lang = "en"
    response = RedirectResponse(url=next, status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=31536000)  # 1 year
    return response

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    lang = get_lang(request)
    request.state.lang = lang
    onboardings = list_onboardings()
    return templates.TemplateResponse("home.html", {"request": request, "onboardings": onboardings, "lang": lang})

@app.get("/onboard", response_class=HTMLResponse)
def onboard_form(request: Request):
    lang = get_lang(request)
    request.state.lang = lang
    return templates.TemplateResponse("create.html", {"request": request, "lang": lang})

@app.post("/onboard")
def onboard_create(
    request: Request,
    employee_name: str = Form(...),
    manager_name: str = Form(...),
    role: str = Form(...),
    grade: str = Form(...),
    start_date: str = Form(...),
    lang: str = Form("en"),
):
    if lang not in ("en", "ja"):
        lang = get_lang(request)
    oid = create_onboarding(employee_name, manager_name, role, grade, start_date, lang)
    return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

@app.get("/onboarding/{oid}", response_class=HTMLResponse)
def onboarding_detail(request: Request, oid: str):
    lang = get_lang(request)
    request.state.lang = lang
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)
    
    # Use onboarding's lang if available, otherwise use request lang
    onboarding_lang = onboarding.get("lang", lang)

    # For exec demo: show which template would be used
    start = parse_date(onboarding["start_date"])
    _, plan, template_used = generate(onboarding["role"], onboarding["grade"], start, onboarding_lang)

    tasks = list_tasks(oid)

    class Obj:
        def __init__(self, d): self.__dict__.update(d)

    plan_obj = Obj({"employee": Obj(plan["employee"]), "manager": Obj(plan["manager"])})

    return templates.TemplateResponse(
        "detail.html",
        {"request": request, "onboarding": onboarding, "tasks": tasks, "plan": plan_obj, "template_used": template_used, "lang": onboarding_lang},
    )

@app.post("/onboarding/{oid}/approve")
def approve(request: Request, oid: str):
    lang = get_lang(request)
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)

    if onboarding["status"] != "PENDING":
        return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

    set_status(oid, "APPROVED", None)
    
    # Use onboarding's lang
    onboarding_lang = onboarding.get("lang", lang)
    start = parse_date(onboarding["start_date"])
    tasks_gen, _, _ = generate(onboarding["role"], onboarding["grade"], start, onboarding_lang)

    for t in tasks_gen:
        owner = onboarding["employee_name"] if t.owner == "employee" else onboarding["manager_name"] if t.owner == "manager" else "HR"
        add_task(oid, owner, t.title, t.description, t.due_date.isoformat())

    return RedirectResponse(url=f"/onboarding/{oid}", status_code=303)

@app.get("/onboarding/{oid}/reject", response_class=HTMLResponse)
def reject_form(request: Request, oid: str):
    lang = get_lang(request)
    request.state.lang = lang
    onboarding = get_onboarding(oid)
    if not onboarding:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse("reject.html", {"request": request, "onboarding": onboarding, "lang": lang})

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
    lang = get_lang(request)
    request.state.lang = lang
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
    return templates.TemplateResponse("reminders.html", {"request": request, "tasks": tasks, "messages": [], "lang": lang})

@app.post("/reminders/run", response_class=HTMLResponse)
def reminders_run(request: Request):
    lang = get_lang(request)
    request.state.lang = lang
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
        # Use t function for reminder title
        reminder_title = t("reminders_dm_previews", lang) if lang == "ja" else f"Reminder: {r['title']}"
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

    return templates.TemplateResponse("reminders.html", {"request": request, "tasks": tasks, "messages": messages, "lang": lang})

@app.get("/chat", response_class=HTMLResponse)
def chat(request: Request):
    """WebチャットUI"""
    lang = get_lang(request)
    request.state.lang = lang
    return templates.TemplateResponse("chat.html", {"request": request, "lang": lang})

@app.post("/chat/ask")
async def chat_ask(request: Request):
    """チャット質問を処理"""
    from fastapi import Body
    data = await request.json()
    question = data.get("question", "")
    
    # QAエンジンで処理
    qa_response = process_question(question)
    
    # Block Kit風のblocksを生成
    blocks = create_bot_response(
        text=qa_response.answer_text,
        confidence=qa_response.confidence,
        references=qa_response.references,
        escalate=len(qa_response.suggested_actions) > 0
    )
    
    return {"blocks": blocks}

@app.post("/chat/escalate")
async def chat_escalate(request: Request):
    """Escalate to HR（Webチャットから）"""
    from fastapi import Body
    data = await request.json()
    question = data.get("question", "")
    
    ticket_id = create_ticket(
        source="web",
        question=question,
        user_ref=None
    )
    
    return {"ticket_id": ticket_id, "status": "escalated"}

@app.get("/tickets", response_class=HTMLResponse)
def tickets(request: Request):
    """チケット一覧（HR用）"""
    lang = get_lang(request)
    request.state.lang = lang
    tickets_list = list_tickets()
    return templates.TemplateResponse("tickets.html", {"request": request, "tickets": tickets_list, "lang": lang})

@app.post("/tickets/{ticket_id}/close")
def close_ticket_route(ticket_id: str):
    """チケットをクローズ"""
    close_ticket(ticket_id)
    return RedirectResponse(url="/tickets", status_code=303)

# Slack Events API endpoints
if SLACK_ENABLED:
    @app.post("/slack/events")
    async def slack_events(request: Request):
        """Slack Events API endpoint"""
        return await handler.handle(request)
    
    @app.post("/slack/interactive")
    async def slack_interactive(request: Request):
        """Slack Interactive Components endpoint"""
        return await handler.handle(request)
    
    @app.post("/slack/commands")
    async def slack_commands(request: Request):
        """Slack Slash Commands endpoint"""
        return await handler.handle(request)

# Slack Events API endpoint
if SLACK_ENABLED:
    @app.post("/slack/events")
    async def slack_events(request: Request):
        """Slack Events API endpoint"""
        return await handler.handle(request)
    
    @app.post("/slack/interactive")
    async def slack_interactive(request: Request):
        """Slack Interactive Components endpoint"""
        return await handler.handle(request)
    
    @app.post("/slack/commands")
    async def slack_commands(request: Request):
        """Slack Slash Commands endpoint"""
        return await handler.handle(request)

from __future__ import annotations
from datetime import datetime, timezone, timedelta, date

JST = timezone(timedelta(hours=9))

def now_jst() -> datetime:
    return datetime.now(tz=JST)

def parse_date(s: str) -> date:
    return date.fromisoformat(s)

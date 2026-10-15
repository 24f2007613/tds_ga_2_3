import secrets
from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..settings import Q7_API_KEY, STUDENT_EMAIL

router = APIRouter()


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


@router.post("/analytics")
async def analytics(request: Request):
    key = request.headers.get("x-api-key", "")
    if not key or not secrets.compare_digest(key.encode(), Q7_API_KEY.encode()):
        return JSONResponse({"detail": "invalid or missing API key"}, status_code=401)
    try:
        body = await request.json()
        events = body.get("events", []) if isinstance(body, dict) else []
    except Exception:
        return JSONResponse({"detail": "invalid JSON"}, status_code=400)

    users, per_user, revenue = set(), defaultdict(float), 0.0
    for ev in events:
        if not isinstance(ev, dict):
            continue
        u = ev.get("user")
        users.add(u)
        amt = _num(ev.get("amount"))
        if amt > 0:  # ignore zero and negative amounts
            revenue += amt
            per_user[u] += amt
    top = max(per_user, key=per_user.get) if per_user else None
    return {"email": STUDENT_EMAIL, "total_events": len(events),
            "unique_users": len(users), "revenue": round(revenue, 6), "top_user": top}

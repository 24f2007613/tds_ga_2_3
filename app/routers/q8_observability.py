import time

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from .. import observability as obs
from ..settings import STUDENT_EMAIL
from .q6_redis import redis_status

router = APIRouter()


@router.get("/work")
async def work(n: int = Query(1, ge=0)):
    acc = 0
    for i in range(min(n, 1_000_000)):  # K units of (cheap) work
        acc = (acc * 31 + i) % 1_000_003
    return {"email": STUDENT_EMAIL, "done": n}


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    body = ("# HELP http_requests_total Total HTTP requests received.\n"
            "# TYPE http_requests_total counter\n"
            f"http_requests_total {obs.request_total}\n")
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4")


@router.get("/healthz")
async def healthz():
    # Serves both Q6 (redis ping) and Q8 (uptime_s)
    return {"status": "ok", "uptime_s": time.time() - obs.START,
            "redis": await redis_status()}


@router.get("/logs/tail")
async def logs_tail(limit: int = Query(50, ge=1, le=2000)):
    return list(obs.logs)[-limit:]

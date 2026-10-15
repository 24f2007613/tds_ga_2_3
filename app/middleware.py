import json
import time
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from . import observability as obs
from .settings import Q3_ALLOWED_ORIGIN

EXPOSE = "X-Request-ID, X-Process-Time"


def _cors_headers(request: Request) -> dict:
    """Per-path CORS. /stats = strict single origin (no wildcard); everything else = *."""
    origin = request.headers.get("origin")
    if not origin:
        return {}
    if request.url.path == "/stats":
        if origin == Q3_ALLOWED_ORIGIN:
            return {"Access-Control-Allow-Origin": origin, "Vary": "Origin",
                    "Access-Control-Expose-Headers": EXPOSE}
        return {"Vary": "Origin"}
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": EXPOSE}


async def core_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    rid = str(uuid.uuid4())
    obs.request_total += 1  # every request (incl. preflight, /metrics) counts

    cors = _cors_headers(request)
    origin = request.headers.get("origin")

    if request.method == "OPTIONS" and request.headers.get("access-control-request-method"):
        if "Access-Control-Allow-Origin" in cors:
            resp = Response(status_code=204)
            resp.headers.update(cors)
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = request.headers.get(
                "access-control-request-headers", "*")
            resp.headers["Access-Control-Max-Age"] = "600"
        else:  # disallowed origin: reject, no ACAO header
            resp = Response(status_code=403, content="CORS origin not allowed")
        status = resp.status_code
    else:
        try:
            resp = await call_next(request)
        except Exception:
            resp = JSONResponse({"detail": "internal error"}, status_code=500)
        resp.headers.update(cors)
        status = resp.status_code

    resp.headers["X-Request-ID"] = rid
    resp.headers["X-Process-Time"] = f"{time.perf_counter() - t0:.6f}"

    entry = {"level": "info" if status < 500 else "error", "ts": time.time(),
             "method": request.method, "path": request.url.path,
             "status": status, "request_id": rid}
    obs.logs.append(entry)
    print(json.dumps(entry), flush=True)
    return resp

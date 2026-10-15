from fastapi import FastAPI

from .middleware import core_middleware
from .routers import q3_stats, q4_verify, q5_config, q6_redis, q7_analytics, q8_observability

app = FastAPI(title="TDS GA2 - Q3 to Q8")
app.middleware("http")(core_middleware)

for r in (q3_stats, q4_verify, q5_config, q6_redis, q7_analytics, q8_observability):
    app.include_router(r.router)


@app.get("/")
async def root():
    return {"service": "tds-ga2", "endpoints": [
        "GET /stats", "POST /verify", "GET /effective-config", "POST /hit/{key}",
        "GET /count/{key}", "POST /analytics", "GET /work", "GET /metrics",
        "GET /healthz", "GET /logs/tail"]}

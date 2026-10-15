# TDS GA2 – Q3 to Q8 (single FastAPI service)

| Q | Endpoint(s) | File |
|---|-------------|------|
| 3 | `GET /stats` (+ strict CORS, X-Request-ID, X-Process-Time) | `app/routers/q3_stats.py`, `app/middleware.py` |
| 4 | `POST /verify` | `app/routers/q4_verify.py` |
| 5 | `GET /effective-config` | `app/routers/q5_config.py` |
| 6 | `POST /hit/{key}`, `GET /count/{key}`, `GET /healthz` | `app/routers/q6_redis.py`, `docker-compose.yml` |
| 7 | `POST /analytics` | `app/routers/q7_analytics.py` |
| 8 | `GET /work`, `/metrics`, `/healthz`, `/logs/tail` | `app/routers/q8_observability.py` |

## Before you deploy – 3 things to set
1. `STUDENT_EMAIL` = your exam login email (Render env var).
2. Paste the Q4 public key into `app/config/idp_public_key.pem` (or set env `OIDC_PUBLIC_KEY`).
3. Double-check the values I transcribed from screenshots against the exam page:
   `Q3_ALLOWED_ORIGIN`, `OIDC_AUDIENCE`, `Q7_API_KEY` (env vars, defaults in `app/settings.py`),
   and `app/config/config.development.yaml`, `app/config/.env`, `ASSIGNED_OS_ENV` (Q5).

## Deploy on Render
Push to GitHub -> Render -> New -> Blueprint (uses `render.yaml`; also creates a free Key Value/Redis).
Or manually: Python web service, build `pip install -r requirements.txt`,
start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Keep ONE worker.

Submit URLs:
- Q3: `https://<app>.onrender.com`
- Q4: `https://<app>.onrender.com/verify`
- Q5: `https://<app>.onrender.com/effective-config`
- Q7: `https://<app>.onrender.com/analytics`
- Q8: `https://<app>.onrender.com`

## Q6 (compose + tunnel)
```
docker compose up --build
cloudflared tunnel --url http://localhost:8000   # paste the trycloudflare URL
```

## Tests
`pip install -r requirements-dev.txt && pytest`

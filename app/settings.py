"""All per-student values live here. Override any of them with environment variables
(Render dashboard -> Environment) instead of editing code."""
import os
from pathlib import Path

BASE = Path(__file__).parent

# ---- Your logged-in exam email (used by Q3, Q7, Q8) ----------------------------
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL", "CHANGE_ME@example.com")

# ---- Q3: strict per-origin CORS -------------------------------------------------
Q3_ALLOWED_ORIGIN = os.getenv("Q3_ALLOWED_ORIGIN", "https://dash-t3xuf4.example.com")

# ---- Q4: OIDC verification ------------------------------------------------------
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "https://idp.exam.local")
OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE", "tds-mz0o1f8p.apps.exam.local")


def load_public_key() -> str:
    env = os.getenv("OIDC_PUBLIC_KEY")
    if env:
        return env.replace("\\n", "\n")
    p = BASE / "config" / "idp_public_key.pem"
    return p.read_text() if p.exists() else ""


# ---- Q5: config layers ----------------------------------------------------------
CONFIG_ENV = os.getenv("CONFIG_ENV", "development")  # -> config/config.<env>.yaml
DEFAULTS = {"port": 8000, "workers": 1, "debug": False,
            "log_level": "info", "api_key": "default-secret-000"}
# The "OS env vars (APP_* prefix)" layer assigned on the exam page. Real OS env wins.
ASSIGNED_OS_ENV = {"APP_WORKERS": "1"}

# ---- Q6: Redis ------------------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ---- Q7: analytics API key ------------------------------------------------------
Q7_API_KEY = os.getenv("Q7_API_KEY", "ak_33h2xi1ieu8vtosuib0g6ehoi")

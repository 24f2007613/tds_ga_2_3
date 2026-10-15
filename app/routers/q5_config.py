import os
from typing import Any

import yaml
from fastapi import APIRouter, Request

from ..settings import ASSIGNED_OS_ENV, BASE, CONFIG_ENV, DEFAULTS

router = APIRouter()
ALIASES = {"num_workers": "workers"}
INT_KEYS = {"port", "workers"}


def _norm(key: str) -> str:
    k = key.strip().lower().replace("-", "_")
    return ALIASES.get(k, k)


def _yaml_layer() -> dict:
    p = BASE / "config" / f"config.{CONFIG_ENV}.yaml"
    if not p.exists():
        return {}
    data = yaml.safe_load(p.read_text()) or {}
    return {_norm(str(k)): v for k, v in data.items()}


def _dotenv_layer() -> dict:
    p = BASE / "config" / ".env"
    out = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k.upper().startswith("APP_"):
            k = k[4:]
        out[_norm(k)] = v.strip().strip('"').strip("'")
    return out


def _os_layer() -> dict:
    env = {**ASSIGNED_OS_ENV, **{k: v for k, v in os.environ.items() if k.startswith("APP_")}}
    return {_norm(k[4:]): v for k, v in env.items() if k.upper().startswith("APP_")}


def _cli_layer(request: Request) -> dict:
    out = {}
    for k, v in request.query_params.multi_items():
        kl = k.lower()
        if kl == "set" and "=" in v:            # ?set=port=8851&set=debug=true
            key, val = v.split("=", 1)
            out[_norm(key)] = val
        elif kl.startswith("set-") and len(k) > 4:  # ?set-port=8851 (also accepted)
            out[_norm(k[4:])] = v
    return out


def _to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"true", "1", "yes", "on"}


def _coerce(key: str, v: Any) -> Any:
    if key in INT_KEYS:
        try:
            return int(str(v).strip())
        except ValueError:
            return v
    if key == "debug":
        return _to_bool(v)
    return str(v)


@router.get("/effective-config")
async def effective_config(request: Request):
    merged: dict = {}
    for layer in (DEFAULTS, _yaml_layer(), _dotenv_layer(), _os_layer(), _cli_layer(request)):
        merged.update(layer)  # later layers win: defaults<yaml<.env<OS env<CLI
    result = {k: _coerce(k, v) for k, v in merged.items()}
    result["api_key"] = "*****"  # never expose the real secret
    return result

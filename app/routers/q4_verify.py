import logging

import jwt
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..settings import OIDC_AUDIENCE, OIDC_ISSUER, load_public_key

router = APIRouter()
log = logging.getLogger("verify")


def _invalid():
    return JSONResponse({"valid": False}, status_code=401)


@router.post("/verify")
async def verify(request: Request):
    try:
        body = await request.json()
        token = body.get("token") if isinstance(body, dict) else None
        if not isinstance(token, str) or not token:
            return _invalid()
        claims = jwt.decode(
            token,
            load_public_key(),
            algorithms=["RS256"],          # never accept HS256 / none
            audience=OIDC_AUDIENCE,        # aud check
            issuer=OIDC_ISSUER,            # iss check
            options={"require": ["exp", "iss", "aud"], "verify_exp": True},
        )
    except Exception as e:  # signature, expiry, aud, iss, malformed, bad key...
        info = {}
        try:
            info = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            pass
        print("VERIFY_REJECTED", type(e).__name__, str(e)[:200],
              "| token iss/aud/exp:", info.get("iss"), info.get("aud"), info.get("exp"),
              "| expected iss/aud:", OIDC_ISSUER, OIDC_AUDIENCE,
              "| key_loaded:", "PASTE_THE_PUBLIC_KEY" not in load_public_key(), flush=True)
        return _invalid()
    return {"valid": True, "email": claims.get("email"),
            "sub": claims.get("sub"), "aud": claims.get("aud")}

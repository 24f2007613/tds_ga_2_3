import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException

from ..settings import REDIS_URL

router = APIRouter()
_client = None


def get_redis():
    global _client
    if _client is None:
        _client = aioredis.from_url(REDIS_URL, decode_responses=True,
                                    socket_connect_timeout=2, socket_timeout=2)
    return _client


async def redis_status() -> str:
    try:
        return "up" if await get_redis().ping() else "down"
    except Exception:
        return "down"


@router.post("/hit/{key}")
async def hit(key: str):
    try:
        n = await get_redis().incr(f"counter:{key}")  # atomic INCR
    except Exception:
        raise HTTPException(503, "redis unavailable")
    return {"key": key, "count": int(n)}


@router.get("/count/{key}")
async def count(key: str):
    try:
        v = await get_redis().get(f"counter:{key}")
    except Exception:
        raise HTTPException(503, "redis unavailable")
    return {"key": key, "count": int(v) if v else 0}

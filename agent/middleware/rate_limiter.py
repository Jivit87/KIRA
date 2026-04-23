from fastapi import Request, HTTPException
from memory.redis_client import r

# Max messages allowed per minute
RATE_LIMIT = 60
WINDOW_SEC = 60


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware that blocks requests if more than 60 messages
    are sent in a 60-second window. Only applies to the /message endpoint.
    """
    if request.url.path == "/message":
        key = "rate:agent:global"

        # Increment the counter and set expiry on first hit
        count = r.incr(key)
        if count == 1:
            r.expire(key, WINDOW_SEC)

        if count > RATE_LIMIT:
            ttl = r.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit hit. Resets in {ttl}s."
            )

    return await call_next(request)

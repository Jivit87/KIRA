import redis
import json
import os

r = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True  # returns strings instead of bytes
)


# ── Confirmation helpers ──────────────────────────────────────────────────────
# Used when a risky action needs a YES/NO reply before executing

def set_confirmation(sender: str, payload: dict, ttl: int = 120):
    # Store a pending confirmation. Auto-expires in 2 minutes.
    r.setex(f"confirm:{sender}", ttl, json.dumps(payload))

def get_confirmation(sender: str) -> dict | None:
    # Get the pending confirmation for a sender, or None if expired/missing.
    data = r.get(f"confirm:{sender}")
    return json.loads(data) if data else None

def clear_confirmation(sender: str):
    # Delete the pending confirmation (after YES/NO is received).
    r.delete(f"confirm:{sender}")


# ── Rate limit helper ─────────────────────────────────────────────────────────
# Sliding window: max 60 messages per 60 seconds

def check_rate_limit(key: str = "rate:agent:global", limit: int = 60, window: int = 60) -> bool:
    """
    Returns True if the request is within the rate limit.
    Returns False if the limit has been exceeded.
    """
    pipe = r.pipeline()
    pipe.incr(key)       # increment counter
    pipe.expire(key, window)  # reset window every 60s
    count, _ = pipe.execute()
    return count <= limit

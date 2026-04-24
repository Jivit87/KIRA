import redis
import json
import os

# Redis connection for storing paused plan state
r = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

TTL = 300  # plan state expires after 5 minutes of inactivity


def save_plan_state(sender: str, plan: dict, step_index: int, context: dict):
    """
    Save the current plan execution state so it can be resumed.
    Called when a step uses ask_user and we need to wait for a reply.
    """
    r.setex(
        f"plan:{sender}",
        TTL,
        json.dumps({
            "plan":       plan,
            "step_index": step_index,  # which step to resume from
            "context":    context      # results from completed steps
        })
    )


def get_plan_state(sender: str) -> dict | None:
    """Get the paused plan state for a sender, or None if none exists."""
    data = r.get(f"plan:{sender}")
    return json.loads(data) if data else None


def clear_plan_state(sender: str):
    """Delete the plan state (after plan completes or is cancelled)."""
    r.delete(f"plan:{sender}")

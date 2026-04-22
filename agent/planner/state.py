import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

TTL = 300  # 5 minutes

def save_plan_state(sender, plan, step_index, context):
    r.setex(
        f"plan:{sender}",
        TTL,
        json.dumps({
            "plan": plan,
            "step_index": step_index,
            "context": context
        })
    )

def get_plan_state(sender):
    data = r.get(f"plan:{sender}")
    return json.loads(data) if data else None

def clear_plan_state(sender):
    r.delete(f"plan:{sender}")
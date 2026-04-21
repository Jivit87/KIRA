import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

TTL = 120 # sec

def store_confirmation(msg_id: str, action_data: dict):
    r.setex(f"confirm:{msg_id}", TTL, json.dumps(action_data))

def get_confirmation(msg_id: str):
    data = r.get(f"confirm:{msg_id}")
    if data:
        return json.loads(data)
    return None

def clear_confirmation(msg_id: str):
    r.delete(f"confirm:{msg_id}")
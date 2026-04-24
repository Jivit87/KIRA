from memory.redis_client import set_confirmation, get_confirmation, clear_confirmation
from streaming import stream_status

# Re-export so main.py can import from here directly
__all__ = ["store_confirmation", "get_confirmation", "clear_confirmation", "request_confirmation"]


def store_confirmation(sender: str, payload: dict):
    # Save a pending risky action to Redis (expires in 2 minutes).
    set_confirmation(sender, payload)


async def request_confirmation(sender: str, tool_name: str, params: dict, reason: str):
    """
    Store the pending action and send a YES/NO prompt to WhatsApp.
    The action will be executed when the user replies YES.
    """
    # Save what we're waiting to execute
    store_confirmation(sender, {
        "tool":   tool_name,
        "params": params
    })

    # Ask the user
    await stream_status(
        f"⚠️ Risky action detected:\n"
        f"Tool: {tool_name}\n"
        f"Reason: {reason}\n\n"
        f"Reply YES to run it or NO to cancel.\n"
        f"(Auto-cancels in 2 minutes)"
    )

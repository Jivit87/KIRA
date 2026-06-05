import httpx
from utils.formatter import format_reply

BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"


async def stream_status(text: str):
    # Send an immediate status update to WhatsApp.
    text = format_reply(text)
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            await client.post(BAILEYS_SEND_URL, json={"text": text})
        except Exception as e:
            print(f"⚠️ stream_status failed: {e}")

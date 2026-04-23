import httpx

BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"


async def stream_status(text: str):
    # Send an immediate status update to WhatsApp.
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            await client.post(BAILEYS_SEND_URL, json={"text": text})
        except Exception as e:
            print(f"⚠️ stream_status failed: {e}")

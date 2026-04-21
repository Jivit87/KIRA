import httpx

BAILEYS_URL = "http://localhost:8766/send"

async def stream_status(text: str, to: str):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(BAILEYS_URL, json={
                "text": text,
                "to": to
            })
    except Exception as e:
        print("Streaming error:", e)
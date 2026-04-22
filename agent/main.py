import os
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import handle_message

app = FastAPI()


# Shape of the incoming message from Baileys
class Message(BaseModel):
    text: str
    msg_id: str


@app.post("/message")
async def receive_message(msg: Message):
    """Baileys POSTs here when you send a message to yourself on WhatsApp."""
    await handle_message(msg.text, msg.msg_id)
    return {"ok": True}


@app.get("/health")
async def health():
    """Simple health check — visit http://127.0.0.1:8765/health to verify it's running."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)

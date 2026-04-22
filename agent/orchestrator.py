import os
import httpx
from groq import Groq

# URL of the Baileys sender — Python sends replies here
BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"

# Groq client (replaces Ollama as the LLM provider)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful Mac assistant the user chats with via WhatsApp.
Be concise. Plain text only — no markdown."""


async def send(text: str):
    """Send a message back to WhatsApp via Baileys."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(BAILEYS_SEND_URL, json={"text": text})
        except Exception as e:
            print(f"❌ Failed to send reply: {e}")


async def handle_message(text: str, msg_id: str):
    """
    Phase 1: Simple chat — just send the message to the LLM and reply.
    No tools, no memory, no intent classification yet.
    """
    try:
        response = groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": text}
            ]
        )
        reply = response.choices[0].message.content
        await send(reply)

    except Exception as e:
        print(f"❌ LLM error: {e}")
        await send("⚠️ Something went wrong. Try again.")

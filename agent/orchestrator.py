import os
import httpx
from groq import Groq
from memory.mem0_client import add_memory, search_memory
from memory.redis_client import check_rate_limit

BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"

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
    Phase 2: Chat with memory.
    1. Rate limit check
    2. Search past memory for relevant context
    3. Inject context into the prompt
    4. Call LLM and reply
    5. Save the exchange to memory
    """
    # 1. Rate limit — max 60 messages per minute
    if not check_rate_limit():
        await send("⏸ Rate limit hit. Please slow down.")
        return

    # 2. Search memory for anything relevant to this message
    mem_results = search_memory(text, limit=5)

    # Build a plain string from the memory results
    memory_context = "\n".join(
        m.get("memory", "")
        for m in mem_results
        if isinstance(m, dict) and m.get("memory")
    )

    # 3. Build the system prompt — inject memory if we have any
    system = SYSTEM_PROMPT
    if memory_context:
        system += f"\n\nRelevant past context:\n{memory_context}"

    # 4. Call the LLM
    try:
        response = groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": text}
            ]
        )
        reply = response.choices[0].message.content

    except Exception as e:
        print(f"❌ LLM error: {e}")
        await send("⚠️ Something went wrong. Try again.")
        return

    # reply back to WhatsApp
    await send(reply)

    # Save this exchange to memory (only if message is meaningful) -> no saving ok, hi etc..
    if len(text.strip()) > 3:
        add_memory(text, reply)

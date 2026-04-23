import os
import httpx
from groq import Groq
from memory.mem0_client import add_memory, search_memory
from memory.redis_client import check_rate_limit
from intent.classifier import classify_intent
from streaming import stream_status

BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CHAT_SYSTEM = """You are a helpful assistant the user chats with via WhatsApp.
Be conversational, warm, and concise. Plain text only — no markdown."""

# Used for action/plan mode — task-focused
ACTION_SYSTEM = """You are a Mac automation assistant the user controls via WhatsApp.
Be concise. Plain text only. Keep replies short — user is on mobile."""


async def send(text: str):
    # Send a message back to WhatsApp via Baileys.
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(BAILEYS_SEND_URL, json={"text": text})
        except Exception as e:
            print(f"❌ Failed to send reply: {e}")


async def llm_reply(text: str, system: str, memory_context: str = "") -> str:
    # Call Groq and return the reply text.
    # Inject memory into the system prompt if we have any
    if memory_context:
        system += f"\n\nRelevant past context:\n{memory_context}"

    response = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": text}
        ]
    )
    return response.choices[0].message.content


async def handle_message(text: str, msg_id: str):
    """
    Phase 3: Classify intent, route to the right handler, stream status.

    Flow:
      1. Rate limit check
      2. Search memory for context
      3. Classify intent → chat / action / plan
      4. Route:
           chat   → LLM reply directly
           action → stream "⏳ On it..." → LLM reply (tools wired in Phase 4)
           plan   → stream "🧠 Planning..." → LLM reply (planner wired in Phase 5)
      5. Save exchange to memory
    """
    # 1. Rate limit check
    if not check_rate_limit():
        await send("⏸ Rate limit hit. Please slow down.")
        return

    # 2. Search memory
    mem_results = search_memory(text, limit=5)
    memory_context = "\n".join(
        m.get("memory", "")
        for m in mem_results
        if isinstance(m, dict) and m.get("memory")
    )

    # 3. Classify intent
    intent = classify_intent(text).get("intent", "chat")
    print(f"🧠 Intent: {intent}")

    reply = ""

    try:
        # 4. Route by intent
        if intent == "chat":
            # respond directly from llm
            reply = await llm_reply(text, CHAT_SYSTEM, memory_context)
            await send(reply)

        elif intent == "action":
            # Single task — stream a status first so user isn't waiting in silence
            await stream_status("⏳ On it...")
            # TODO Phase 4: replace with actual tool call
            reply = await llm_reply(text, ACTION_SYSTEM, memory_context)
            await send(reply)

        elif intent == "plan":
            # Multi-step task — stream a status first
            await stream_status("🧠 Planning...")
            # TODO Phase 5: replace with planner → executor loop
            reply = await llm_reply(text, ACTION_SYSTEM, memory_context)
            await send(reply)

        else:
            reply = "🤖 Not sure what you mean."
            await send(reply)

    except Exception as e:
        print(f"❌ Error handling message: {e}")
        await send("⚠️ Something went wrong. Try again.")
        return

    # 5. Save to memory (skip very short messages like "yes" / "no")
    if len(text.strip()) > 3 and reply:
        add_memory(text, reply)

import os
import json
import httpx
from groq import Groq
from memory.mem0_client import add_memory, search_memory
from memory.redis_client import check_rate_limit, get_confirmation, clear_confirmation
from intent.classifier import classify_intent
from streaming import stream_status
from utils.risk_detector import is_risky
from confirmation import request_confirmation
from tool_intelligence.router import intelligent_tool_call
from planner.planner import create_plan
from planner.executor import execute_plan
from planner.state import get_plan_state, clear_plan_state

BAILEYS_SEND_URL = "http://127.0.0.1:8766/send"

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CHAT_SYSTEM = """You are a helpful assistant the user chats with via WhatsApp.
Be conversational, warm, and concise. Plain text only — no markdown."""

ACTION_SYSTEM = """You are a Mac automation assistant the user controls via WhatsApp.
The user wants to perform a task on their Mac.
Choose the right tool and respond with a JSON tool call.

Available tools:
  spotify_control(action, query)
  vscode_open(path)
  terminal_run(command)
  filesystem_op(operation, path, destination, query)
  system_control(action, value)
  browser_open(url, query)
  app_control(action, app_name)
  clipboard_read()
  clipboard_write(content)
  calendar_query(query)
  reminder_create(title, notes)
  send_notification(title, message, sound)
  screen_capture(region)

Respond ONLY with JSON:
{"tool": "tool_name", "params": {"param1": "value1"}}
"""


async def send(text: str):
    """Send a message back to WhatsApp via Baileys."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(BAILEYS_SEND_URL, json={"text": text})
        except Exception as e:
            print(f"❌ Failed to send reply: {e}")


async def llm_chat(text: str, memory_context: str = "") -> str:
    """Plain chat reply — no tools."""
    system = CHAT_SYSTEM
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


async def handle_action(text: str, sender: str, memory_context: str) -> str:
    """
    Action mode: ask the LLM which tool to use, check risk, then run it.
    Returns the reply string (or empty string if waiting for confirmation).
    """
    system = ACTION_SYSTEM
    if memory_context:
        system += f"\n\nRelevant past context:\n{memory_context}"

    # Ask the LLM to pick a tool and params
    response = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": text}
        ],
        response_format={"type": "json_object"},
    )

    try:
        tool_call = json.loads(response.choices[0].message.content)
        tool_name = tool_call.get("tool", "")
        params    = tool_call.get("params", {})
    except Exception:
        # LLM didn't return valid JSON — fall back to chat
        reply = await llm_chat(text, memory_context)
        await send(reply)
        return reply

    if not tool_name:
        reply = await llm_chat(text, memory_context)
        await send(reply)
        return reply

    # Check if this action is risky
    risky, reason = is_risky(tool_name, params)

    if risky:
        # Store and ask for confirmation — don't run yet
        await request_confirmation(sender, tool_name, params, reason)
        return ""  # waiting for YES/NO

    # Safe — run it
    await stream_status(f"⏳ Running {tool_name}...")
    result = await intelligent_tool_call(tool_name, params)

    if result["error"]:
        reply = f"❌ Failed: {result['error']}"
    else:
        reply = f"✅ {result['output']}"

    await send(reply)
    return reply


async def handle_message(text: str, msg_id: str):
    """
    Main message handler — routes every incoming WhatsApp message.

    Flow:
      1. Rate limit check
      2. Check if a plan is paused waiting for user reply
      3. Check if a risky action is waiting for YES/NO
      4. Search memory for context
      5. Classify intent → chat / action / plan
      6. Route to the right handler
      7. Save exchange to memory
    """
    user_text = text.lower().strip()

    # 1. Rate limit
    if not check_rate_limit():
        await send("⏸ Rate limit hit. Please slow down.")
        return

    # 2. Check for a paused plan waiting for user input (ask_user step)
    plan_state = get_plan_state(msg_id)
    if plan_state:
        if user_text not in ("yes", "no") and not text.strip():
            await send("⚠️ Please reply to continue the paused task.")
            return

        if user_text == "no":
            clear_plan_state(msg_id)
            await send("⛔ Plan cancelled.")
            return

        # Any reply (including "yes") resumes the plan
        plan       = plan_state["plan"]
        step_index = plan_state["step_index"]
        context    = plan_state["context"]
        clear_plan_state(msg_id)

        await stream_status("🔄 Resuming plan...")
        await execute_plan(plan, msg_id, start_index=step_index, context=context)
        return

    # 3. Check for a pending YES/NO confirmation (risky action)
    if user_text in ("yes", "no"):
        pending = get_confirmation(msg_id)

        if pending:
            clear_confirmation(msg_id)

            if user_text == "no":
                await send("⛔ Action cancelled.")
                return

            # YES — run the stored action
            await stream_status("⏳ Running confirmed action...")
            result = await intelligent_tool_call(pending["tool"], pending["params"])

            if result["error"]:
                await send(f"❌ Failed: {result['error']}")
            else:
                await send(f"✅ {result['output']}")
            return

    # 4. Search memory for relevant context
    mem_results = search_memory(text, limit=5)
    memory_context = "\n".join(
        m.get("memory", "")
        for m in mem_results
        if isinstance(m, dict) and m.get("memory")
    )

    # 5. Classify intent
    intent = classify_intent(text).get("intent", "chat")
    print(f"🧠 Intent: {intent}")

    reply = ""

    try:
        if intent == "chat":
            reply = await llm_chat(text, memory_context)
            await send(reply)

        elif intent == "action":
            await stream_status("⏳ On it...")
            reply = await handle_action(text, msg_id, memory_context)

        elif intent == "plan":
            await stream_status("🧠 Analyzing your goal...")
            # Search memory to give the planner context
            plan = create_plan(text, mem_results)
            step_count = len(plan.get("steps", []))
            await stream_status(f"📋 {step_count}-step plan ready. Starting...")
            await execute_plan(plan, msg_id)
            reply = ""  # executor streams its own status messages

        else:
            reply = "🤖 Not sure what you mean."
            await send(reply)

    except Exception as e:
        print(f"❌ Error: {e}")
        await send("⚠️ Something went wrong. Try again.")
        return

    # 6. Save to memory (skip very short messages and empty replies)
    if len(text.strip()) > 3 and reply:
        add_memory(text, reply)

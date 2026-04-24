import os
import json
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PLANNER_PROMPT = """
You are a Mac automation planner. Break the user's goal into a step-by-step JSON plan.

Each step must have:
  "step":        step number (1, 2, 3...)
  "description": what this step does (shown to user)
  "tool":        which tool to use (see list below)
  "params":      dict of params for that tool
  "critical":    true if failure should abort the whole plan, false to skip and continue

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
  ask_user        — pause and ask the user a question before continuing
  llm_reply       — generate a text summary (no tool, just LLM)

Rules:
  - Keep steps atomic — one tool per step
  - ALWAYS add an ask_user step before any destructive action (delete, rm, etc.)
  - Use llm_reply as the last step to summarize what was done
  - Set critical: true only if the whole plan breaks without this step

Return ONLY valid JSON:
{
  "goal": "...",
  "steps": [
    {"step": 1, "description": "...", "tool": "...", "params": {}, "critical": false}
  ]
}
"""


def create_plan(goal: str, memory_context: list) -> dict:
    """
    Ask the LLM to break a goal into steps.
    memory_context: list of past memory dicts from Mem0
    Returns a plan dict with a "steps" list.
    """
    # Turn memory list into a plain string for the prompt
    context_str = "\n".join(
        m.get("memory", "")
        for m in memory_context
        if isinstance(m, dict) and m.get("memory")
    )

    user_message = f"Goal: {goal}"
    if context_str:
        user_message = f"Memory context:\n{context_str}\n\n{user_message}"

    try:
        response = groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"⚠️ Planner failed: {e}")
        # Fallback: single step that just replies
        return {
            "goal": goal,
            "steps": [
                {
                    "step": 1,
                    "description": "Reply to user",
                    "tool": "llm_reply",
                    "params": {"prompt": goal},
                    "critical": False
                }
            ]
        }

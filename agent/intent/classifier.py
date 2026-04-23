import os
import json
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLASSIFIER_PROMPT = """
You are an intent classifier for a Mac automation assistant.
Classify the user's message into exactly one of:
  - "chat"   : casual conversation, questions, brainstorming
  - "action" : a single clear task (open app, play music, find file)
  - "plan"   : a complex multi-step task (clean my mac, organize downloads)

Respond ONLY with valid JSON: {"intent": "chat"|"action"|"plan"}

Examples:
  "hey what's up"                       -> {"intent": "chat"}
  "play lofi music"                     -> {"intent": "action"}
  "clean my mac and organize downloads" -> {"intent": "plan"}
"""


def classify_intent(message: str) -> dict:
    """
    Returns a dict like {"intent": "chat"} or {"intent": "action"} or {"intent": "plan"}.
    Falls back to "chat" if the LLM response can't be parsed.
    """
    try:
        response = groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user",   "content": message}
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"⚠️ Intent classification failed: {e}")
        return {"intent": "chat"}  # safe fallback

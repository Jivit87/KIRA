import os
from dotenv import load_dotenv
load_dotenv()
import json
from groq import Groq


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLASSIFIER_PROMPT = """
Classify the user message into one of:
- chat → casual conversation
- action → single task (open app, play music)
- plan → multi-step task

Respond ONLY in JSON format:
{"intent": "chat|action|plan"}

Examples:
"hey" → {"intent": "chat"}
"open spotify" → {"intent": "action"}
"clean my mac and organize files" → {"intent": "plan"}
"""

def classify_intent(message: str):
    respond = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": CLASSIFIER_PROMPT},
            {"role": "user", "content": message}
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(respond.choices[0].message.content)
    
    
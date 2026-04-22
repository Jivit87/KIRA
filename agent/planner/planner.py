import os
from groq import Groq
import json

groq_client = Groq()

PLANNER_PROMPT = """
Break the user goal into steps.

Rules:
- Each step must be simple and executable
- One action per step
- Use tools when needed

Tools:
- open_app
- run_terminal
- filesystem
- ask_user
- reply
-research 

Return JSON:
{
  "steps": [
    {"step": 1, "action": "...", "tool": "...", "input": "..."}
  ]
}
"""

def create_plan(goal: str):
    response = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": goal}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {"steps": []}
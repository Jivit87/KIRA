import os
import json
from groq import Groq

class PlannerAgent:

    def __init__(self):
        self.client = Groq()
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def create_plan(self, goal, memory_context=None):

        context_text = ""

        if memory_context:
            # handle mem0 returning list or dict safely
            if isinstance(memory_context, dict):
                memories = memory_context.get("results", [])
            elif isinstance(memory_context, list):
                memories = memory_context
            else:
                memories = []

            context_text = "\n".join(
                str(m.get("memory", ""))
                for m in memories
                if isinstance(m, dict)
            )

        PLANNER_PROMPT = f"""
You are a task planner.

Break the user's goal into steps.

Each step MUST include:
- step
- action
- agent
- tool
- input

Available agents:
- research
- tools

Rules:
- Use research agent for information gathering.
- Use tools agent for app control / execution.
- Use ask_user if confirmation is needed.
- One action per step.

Return ONLY valid JSON.

Example:

{{
 "steps":[
   {{
     "step":1,
     "action":"Research best Python scraping libraries",
     "agent":"research",
     "tool":"web_search",
     "input":"best Python scraping libraries"
   }},
   {{
     "step":2,
     "action":"Open VS Code",
     "agent":"tools",
     "tool":"open_app",
     "input":"open vscode"
   }}
 ]
}}

Relevant memory:
{context_text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": PLANNER_PROMPT
                },
                {
                    "role": "user",
                    "content": goal
                }
            ]
        )

        raw = response.choices[0].message.content

        try:
            plan = json.loads(raw)
            return plan

        except Exception:
            print("⚠️ Plan parse failed")

            # fallback plan
            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "Handle request directly",
                        "agent": "tools",
                        "tool": "reply",
                        "input": goal
                    }
                ]
            }


    async def summarize(self, results):

        summary_prompt = f"""
Summarize these task results for a user.

Keep it concise and practical.

Results:
{json.dumps(results, indent=2)}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": summary_prompt
                }
            ]
        )

        return response.choices[0].message.content
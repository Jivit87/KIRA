import re
import os
import json
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Layer 1: Hard-coded patterns that are ALWAYS risky — no LLM needed
# These are instant, infallible checks for truly dangerous commands
HARD_RISKY_PATTERNS = [
    r"rm\s+-rf",          # recursive force delete
    r"\bsudo\b",          # superuser command
    r"chmod\s+[0-7]*7[0-7]*",  # world-writable permissions
    r"DROP\s+TABLE",      # SQL table deletion
    r"kill\s+-9",         # force kill process
    r"mkfs",              # format a disk
    r"dd\s+if=",          # disk copy (can wipe drives)
    r">\s*/dev/",         # write to device file
    r":\(\)\{.*\}",       # fork bomb
]

# Layer 2: Groq scores ambiguous commands as low / medium / high
RISK_SCORER_PROMPT = """
You are a shell command risk classifier.
Given a shell command, rate its risk level:
  "low"    — read-only, no side effects, easily reversible (ls, cat, git status)
  "medium" — writes files, installs packages, network requests (npm install, cp)
  "high"   — deletes files, changes permissions, modifies system state (rm, chmod)

Respond ONLY with JSON: {"risk": "low"|"medium"|"high", "reason": "..."}
"""


def is_risky(tool_name: str, params: dict) -> tuple[bool, str]:
    """
    Returns (is_risky: bool, reason: str).

    Two layers:
      1. Filesystem delete → always risky
      2. Terminal commands → regex hard check, then Groq scoring
      3. Everything else → not risky
    """
    # Filesystem delete is always risky
    if tool_name == "filesystem_op" and params.get("operation") == "delete":
        return True, "Filesystem delete operation"

    # Terminal commands go through both layers
    if tool_name == "terminal_run":
        command = str(params.get("command", ""))

        # Layer 1: check hard-coded dangerous patterns
        for pattern in HARD_RISKY_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True, f"Dangerous pattern detected: {pattern}"

        # Layer 2: ask Groq to score the command
        try:
            response = groq_client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": RISK_SCORER_PROMPT},
                    {"role": "user",   "content": f"Command: {command}"}
                ],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            risk_level = result.get("risk", "high")

            if risk_level == "high":
                return True, result.get("reason", "Groq rated high risk")

            return False, result.get("reason", "")

        except Exception as e:
            # If Groq fails, default to risky to be safe
            return True, f"Risk check failed, defaulting to risky: {e}"

    # All other tools are not risky
    return False, ""

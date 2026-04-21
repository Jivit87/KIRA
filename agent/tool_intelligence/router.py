import asyncio
from tools.router import run_action

MAX_RETRIES = 2

async def intelligent_tool_call(input_text: str):
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = run_action(input_text)

            # simulate failure detection
            if result.startswith("❌"):
                raise Exception(result)

            return {
                "output": result,
                "error": None
            }

        except Exception as e:
            last_error = str(e)

            await asyncio.sleep(1 * (2 ** attempt))  # exponential backoff => 1s → 2s → 4s → stop

    return {
        "output": None,
        "error": last_error
    }
import asyncio
from tools.router import call_tool

# If a tool fails, try this fallback tool instead
FALLBACK_MAP = {
    "browser_open":    "app_control",   # open browser app if URL open fails
    "vscode_open":     "app_control",   # open VS Code app if CLI fails
    "spotify_control": "app_control",   # open Spotify app if AppleScript fails
}

MAX_RETRIES = 2       # retry up to 2 times before giving up
RETRY_DELAY = 1.0     # wait 1s, then 2s (exponential backoff)


async def intelligent_tool_call(tool_name: str, params: dict) -> dict:
    """
    Calls a tool with retry logic and fallback.
    Returns {"output": "...", "error": None} on success
    Returns {"output": None, "error": "..."} on failure
    """
    last_error = None

    # Try the tool up to MAX_RETRIES + 1 times
    for attempt in range(MAX_RETRIES + 1):
        result = call_tool(tool_name, params)

        # Tool returns a string — check if it's an error
        if not result.startswith("❌"):
            return {"output": result, "error": None}

        last_error = result

        # Wait before retrying (1s → 2s → stop)
        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY * (2 ** attempt))

    # Retries exhausted — try the fallback tool
    fallback = FALLBACK_MAP.get(tool_name)
    if fallback:
        # For app fallbacks, pass app_name based on the original tool
        fallback_params = _build_fallback_params(tool_name, params)
        result = call_tool(fallback, fallback_params)

        if not result.startswith("❌"):
            return {"output": result, "error": None}

        last_error = result

    return {"output": None, "error": last_error}


def _build_fallback_params(original_tool: str, original_params: dict) -> dict:
    """Build params for the fallback app_control call."""
    app_names = {
        "browser_open":    "Google Chrome",
        "vscode_open":     "Visual Studio Code",
        "spotify_control": "Spotify",
    }
    return {
        "action":   "open",
        "app_name": app_names.get(original_tool, "Finder")
    }

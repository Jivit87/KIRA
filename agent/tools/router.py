from tools.spotify        import spotify_control
from tools.vscode         import vscode_open
from tools.terminal       import terminal_run
from tools.filesystem     import filesystem_op
from tools.system         import system_control
from tools.browser        import browser_open
from tools.app_control    import app_control
from tools.clipboard      import clipboard_read, clipboard_write
from tools.calendar       import calendar_query, reminder_create
from tools.notifications  import send_notification
from tools.screen         import screen_capture

# Maps tool name (what the LLM returns) → the actual function
TOOL_MAP = {
    "spotify_control":  spotify_control,
    "vscode_open":      vscode_open,
    "terminal_run":     terminal_run,
    "filesystem_op":    filesystem_op,
    "system_control":   system_control,
    "browser_open":     browser_open,
    "app_control":      app_control,
    "clipboard_read":   clipboard_read,
    "clipboard_write":  clipboard_write,
    "calendar_query":   calendar_query,
    "reminder_create":  reminder_create,
    "send_notification": send_notification,
    "screen_capture":   screen_capture,
}


def call_tool(tool_name: str, params: dict) -> str:
    """
    Call a tool by name with the given params dict.
    Returns the tool output string, or an error message.
    """
    fn = TOOL_MAP.get(tool_name)

    if not fn:
        return f"❌ Unknown tool: {tool_name}"

    try:
        return fn(**params)
    except TypeError as e:
        return f"❌ Wrong params for {tool_name}: {e}"
    except Exception as e:
        return f"❌ Tool error: {e}"

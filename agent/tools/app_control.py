import subprocess


def app_control(action: str, app_name: str) -> str:
    """
    Open, quit, or focus any macOS application via AppleScript.
    action:   open | quit | focus
    app_name: exact app name e.g. "Spotify", "Visual Studio Code"
    """
    if action in ("open", "focus"):
        script = f'tell application "{app_name}" to activate'

    elif action == "quit":
        script = f'tell application "{app_name}" to quit'

    else:
        return f"❌ Unknown action: {action}"

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ App error: {result.stderr.strip()}"
    return f"✅ {action.capitalize()}: {app_name}"

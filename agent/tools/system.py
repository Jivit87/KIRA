import subprocess


def system_control(action: str, value: str = "") -> str:
    """
    Control macOS system settings via AppleScript.
    action: volume | sleep | lock | wifi
    value:  number 0-100 for volume, "on"/"off" for wifi
    """
    if action == "volume" and value:
        script = f'set volume output volume {value}'

    elif action == "sleep":
        script = 'tell application "System Events" to sleep'

    elif action == "lock":
        # Cmd+Ctrl+Q locks the screen
        script = 'tell application "System Events" to keystroke "q" using {command down, control down}'

    elif action == "wifi" and value == "on":
        script = 'do shell script "networksetup -setairportpower en0 on"'

    elif action == "wifi" and value == "off":
        script = 'do shell script "networksetup -setairportpower en0 off"'

    else:
        return f"❌ Unknown system action: {action} {value}"

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ System error: {result.stderr.strip()}"
    return f"✅ System: {action} {value}".strip()

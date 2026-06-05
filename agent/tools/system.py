import subprocess


def system_control(action: str, value: str = "") -> str:
    """
    Control macOS system settings via AppleScript.
    action: volume | sleep | lock | wifi | get_date
    value:  0-100 OR low|medium|high|mute for volume; on|off for wifi
    """
    if action == "volume" and value:
        # Map named levels to numeric values
        level_map = {"mute": 0, "low": 25, "medium": 50, "high": 85}
        numeric = level_map.get(str(value).lower(), value)
        script = f'set volume output volume {numeric}'

    elif action == "sleep":
        script = 'tell application "System Events" to sleep'

    elif action == "lock":
        # Cmd+Ctrl+Q locks the screen
        script = 'tell application "System Events" to keystroke "q" using {command down, control down}'

    elif action == "wifi" and value == "on":
        script = 'do shell script "networksetup -setairportpower en0 on"'

    elif action == "wifi" and value == "off":
        script = 'do shell script "networksetup -setairportpower en0 off"'

    elif action == "get_date":
        script = 'do shell script "date \'+%A, %B %d, %Y %H:%M:%S\'"'

    else:
        return f"❌ Unknown system action: {action} {value}"

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ System error: {result.stderr.strip()}"
    return f"✅ System: {action} {value}".strip()

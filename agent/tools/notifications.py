import subprocess


def send_notification(title: str, message: str, sound: bool = True) -> str:
    """
    Send a macOS banner notification.
    title:   bold heading of the notification
    message: body text
    sound:   play a ping sound (default True)
    """
    sound_clause = 'sound name "Ping"' if sound else ""
    script = f'display notification "{message}" with title "{title}" {sound_clause}'

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ Notification error: {result.stderr.strip()}"
    return f"🔔 Notification sent: {title}"

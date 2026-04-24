import subprocess


def spotify_control(action: str, query: str = "") -> str:
    """
    Control Spotify via AppleScript.
    action: play | pause | next | previous | search | volume
    query:  search term OR volume level (0-100)
    """
    if action == "play":
        script = 'tell application "Spotify" to play'

    elif action == "pause":
        script = 'tell application "Spotify" to pause'

    elif action == "next":
        script = 'tell application "Spotify" to next track'

    elif action == "previous":
        script = 'tell application "Spotify" to previous track'

    elif action == "search" and query:
        script = f'tell application "Spotify" to search for "{query}"'

    elif action == "volume" and query:
        script = f'tell application "Spotify" to set sound volume to {query}'

    else:
        return f"❌ Unknown Spotify action: {action}"

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ Spotify error: {result.stderr.strip()}"
    return f"🎵 Spotify: {action}"

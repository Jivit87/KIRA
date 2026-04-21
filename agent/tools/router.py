from tools.app_control import open_app

def run_action(user_text: str):
    text = user_text.lower()

    if "spotify" in text:
        return open_app("Spotify")

    if "code" in text or "vscode" in text:
        return open_app("Visual Studio Code")

    if "chrome" in text:
        return open_app("Google Chrome")

    return "I don’t know how to do that yet"




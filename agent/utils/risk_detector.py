def is_risky(user_text: str):
    text = user_text.lower()

    risky_keyword = ["delete", "format", "rm", "sudo", "shutdown", "restart", "format", "erase", "wipe", "destroy", "kill", "terminate", "uninstall", "remove"]

    return any(word in text for word in risky_keyword)


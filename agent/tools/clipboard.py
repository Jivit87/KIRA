import subprocess


def clipboard_read() -> str:
    """Read whatever is currently in the macOS clipboard."""
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    # Cap at 3000 chars so it fits in a WhatsApp message
    return result.stdout[:3000] if result.stdout else "📋 Clipboard is empty"


def clipboard_write(content: str) -> str:
    """Write text to the macOS clipboard."""
    subprocess.run(["pbcopy"], input=content, text=True)
    return "✅ Copied to clipboard"

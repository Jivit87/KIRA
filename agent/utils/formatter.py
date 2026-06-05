import re

MAX_LENGTH = 3000  # WhatsApp message character limit


def format_reply(text: str) -> str:
    """
    Clean up a reply before sending to WhatsApp.
    - Strips markdown (WhatsApp doesn't render it)
    - Truncates long messages with a note
    """
    if not text:
        return ""

    # Remove common markdown symbols
    text = text.replace("**", "")   # bold
    # Only strip __ when used as markdown delimiters (not inside words like __init__)
    text = re.sub(r'(?<!\w)__(?!\w)', "", text)
    text = text.replace("```", "")  # code blocks
    text = text.replace("`", "")    # inline code
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")  # headers

    # Truncate if too long
    if len(text) > MAX_LENGTH:
        text = text[:MAX_LENGTH - 40] + "\n\n[...message truncated]"

    return text.strip()

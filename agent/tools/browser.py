import subprocess


def browser_open(url: str = "", query: str = "") -> str:
    """
    Open a URL or search Google in the default browser.
    Pass url for a direct link, or query for a Google search.
    Uses macOS 'open' command — no Playwright needed for basic browsing.
    """
    if url:
        target = url
    elif query:
        # URL-encode spaces for Google search
        encoded = query.replace(" ", "+")
        target = f"https://www.google.com/search?q={encoded}"
    else:
        return "❌ Provide a url or query"

    result = subprocess.run(["open", target], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ Browser error: {result.stderr.strip()}"
    return f"✅ Opened: {target}"

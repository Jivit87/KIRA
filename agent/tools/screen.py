import subprocess
import base64
import tempfile
import os


def screen_capture(region: str = "full") -> str:
    """
    Take a screenshot of the screen.
    region: "full" — entire screen
            "window" — lets you click a window to capture

    Returns the image as a base64 string (Baileys can send this as an image).
    """
    # Create a temp file to save the screenshot
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name

    if region == "window":
        # -w lets the user click a window
        subprocess.run(["screencapture", "-w", path])
    else:
        # -x captures silently (no shutter sound)
        subprocess.run(["screencapture", "-x", path])

    # Read the file and encode as base64
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    # Clean up the temp file
    os.unlink(path)

    return b64

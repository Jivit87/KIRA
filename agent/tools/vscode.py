import subprocess


def vscode_open(path: str) -> str:
    """
    Open a file or folder in VS Code.
    Requires the 'code' CLI to be installed (VS Code → Shell Command: Install 'code' command).
    """
    result = subprocess.run(["code", path], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ VS Code error: {result.stderr.strip()}"
    return f"✅ Opened {path} in VS Code"

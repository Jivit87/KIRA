import subprocess


def terminal_run(command: str, timeout: int = 30) -> str:
    """
    Run a shell command and return its output.
    stdout + stderr are both captured and returned.
    Output is capped at 3000 characters to keep WhatsApp messages readable.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,          # allows full shell syntax
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout + result.stderr
        return output[:3000] if output.strip() else "✅ Command ran with no output"

    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after {timeout}s"
    except Exception as e:
        return f"❌ Terminal error: {str(e)}"

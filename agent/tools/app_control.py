import subprocess

def open_app(app_name: str):
    try:
        subprocess.run(["open", "-a", app_name])
        return f"Opened {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}"
import pathlib
import shutil
import send2trash


def filesystem_op(operation: str, path: str, destination: str = "", query: str = "") -> str:
    """
    File system operations.
    operation: list | find | read | move | copy | delete
    path:        target file or folder
    destination: used for move and copy
    query:       used for find (glob pattern, e.g. "*.pdf")
    """
    p = pathlib.Path(path).expanduser()

    if operation == "list":
        if not p.is_dir():
            return f"❌ Not a directory: {path}"
        items = list(p.iterdir())
        return "\n".join(str(i) for i in items[:50]) or "Empty directory"

    elif operation == "find":
        # Search from home directory by default
        matches = list(pathlib.Path("~/").expanduser().rglob(query))[:20]
        return "\n".join(str(m) for m in matches) if matches else "No matches found."

    elif operation == "read":
        if not p.is_file():
            return f"❌ Not a file: {path}"
        return p.read_text()[:3000]

    elif operation == "move":
        dest = pathlib.Path(destination).expanduser()
        p.rename(dest)
        return f"✅ Moved {path} → {destination}"

    elif operation == "copy":
        dest = pathlib.Path(destination).expanduser()
        shutil.copy2(p, dest)
        return f"✅ Copied {path} → {destination}"

    elif operation == "delete":
        # send2trash moves to Trash instead of permanently deleting
        send2trash.send2trash(str(p))
        return f"🗑️ Moved {path} to Trash"

    return f"❌ Unknown operation: {operation}"

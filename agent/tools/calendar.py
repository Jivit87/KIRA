import subprocess


def calendar_query(query: str = "today") -> str:
    """
    Query macOS Calendar for events.
    query: "today" | "tomorrow" | "this week"
    Returns a plain text list of events.
    """
    # AppleScript to get today's events from all calendars
    script = '''
    tell application "Calendar"
        set today to current date
        set eventList to ""
        repeat with c in calendars
            repeat with e in events of c
                set d to start date of e
                if d >= today and d < (today + 86400) then
                    set eventList to eventList & summary of e & " at " & time string of d & "\\n"
                end if
            end repeat
        end repeat
        return eventList
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip() if result.stdout.strip() else "📅 No events found."


def reminder_create(title: str, notes: str = "") -> str:
    """Create a new Reminder in macOS Reminders app."""
    script = f'tell application "Reminders" to make new reminder with properties {{name:"{title}", notes:"{notes}"}}'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        return f"❌ Reminder error: {result.stderr.strip()}"
    return f"✅ Reminder created: {title}"


import re
def parse_query(query):
    query = query.lower().strip()

    # Handle empty queries
    if not query:
        return {"type": "unknown"}

    # First / earliest / oldest activity
    if (
        "earliest" in query
        or "first activity" in query
        or "first event" in query
        or "oldest activity" in query
    ):
        return {"type": "earliest"}

    # Latest single activity
    if (
        "latest activity" in query
        or "latest event" in query
        or "most recent activity" in query
        or "most recent event" in query
        or query == "latest"
    ):
        return {"type": "latest"}

    # Recent activity list
    if (
        "recent activity" in query
        or "recent activities" in query
        or "show recent" in query
        or "show my recent" in query
        or ("last" in query and "activit" in query)
    ):
        return {
            "type": "recent",
            "limit": 10
        }

    # Application name mappings
    application_names = {
        "visual studio code": "Visual Studio Code",
        "vs code": "Visual Studio Code",
        "google chrome": "Google Chrome",
        "chrome": "Google Chrome",
        "brave": "Brave",
        "whatsapp": "WhatsApp",
        "telegram": "Telegram",
        "file explorer": "File Explorer",
        "powershell": "PowerShell",
        "windows terminal": "Windows Terminal"
    }

    # Before / after an application
    for name, application in application_names.items():
        if "before" in query and name in query:
            return {
                "type": "before_application",
                "application": application
            }

        if "after" in query and name in query:
            return {
                "type": "after_application",
                "application": application
            }

    # Context around an event
    context_match = re.search(
        r"(?:around|context of|surrounding)\s+"
        r"(?:event\s+)?(\d+)",
        query
    )

    if context_match:
        return {
            "type": "context",
            "event_id": int(context_match.group(1))
        }

    # Events before a specific event
    before_match = re.search(
        r"(?:before|prior to)\s+(?:event\s+)?(\d+)",
        query
    )

    if before_match:
        return {
            "type": "before",
            "event_id": int(before_match.group(1))
        }

    # Events after a specific event
    after_match = re.search(
        r"(?:after|following)\s+(?:event\s+)?(\d+)",
        query
    )

    if after_match:
        return {
            "type": "after",
            "event_id": int(after_match.group(1))
        }

    # Session queries
    session_match = re.search(
        r"session\s+(\d+)",
        query
    )

    if session_match:
        return {
            "type": "session",
            "session_id": int(session_match.group(1))
        }

    # Activity for today
    if "today" in query:
        for name, application in application_names.items():
            if name in query:
                return {
                    "type": "application_today",
                    "application": application
                }

        return {"type": "today"}

    return {"type": "unknown"}


if __name__ == "__main__":
    test_queries = [
        "What is my latest activity?",
        "What was my first activity?",
        "Show my recent activity",
        "Show my last activities",
        "What was I doing today?",
        "What was I doing in VS Code today?",
        "What was I doing in Brave today?",
        "What happened in session 30?",
        "Show me session 31",
        "What happened before event 251?",
        "What happened after event 251?",
        "What was I doing before opening Brave?",
        "What did I do after opening VS Code?",
        "What happened around event 251?"
    ]

    for query in test_queries:
        print(f"{query} -> {parse_query(query)}")

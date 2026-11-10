
import re
from datetime import date, datetime


def parse_query(query):
    query = query.lower().strip()

    if not query:
        return {"type": "unknown"}

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

    # Most-used application
    if (
        "most used" in query
        or "use most" in query
        or "used most" in query
        or "highest usage" in query
        or "top applications" in query
        or "application usage" in query
        or "app usage" in query
    ):
        return {"type": "most_used"}

    # First / earliest activity
    if (
        "earliest" in query
        or "first activity" in query
        or "first event" in query
        or "oldest activity" in query
    ):
        return {"type": "earliest"}

    # Latest activity
    if (
        "latest activity" in query
        or "latest event" in query
        or "most recent activity" in query
        or "most recent event" in query
        or query == "latest"
    ):
        return {"type": "latest"}

    # Recent activity
    if (
        "recent activity" in query
        or "recent activities" in query
        or "show recent" in query
        or "show my recent" in query
        or ("last" in query and "activit" in query)
    ):
        return {"type": "recent", "limit": 10}

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
    session_match = re.search(r"session\s+(\d+)", query)

    if session_match:
        return {
            "type": "session",
            "session_id": int(session_match.group(1))
        }

    # Specific date queries
    months = (
        "january|february|march|april|may|june|"
        "july|august|september|october|november|december"
    )

    date_match = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+"
        rf"({months})(?:\s+(\d{{4}}))?\b",
        query
    )

    if not date_match:
        date_match = re.search(
            rf"\b({months})\s+(\d{{1,2}})"
            rf"(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?\b",
            query
        )

        if date_match:
            month = datetime.strptime(
                date_match.group(1), "%B"
            ).month
            day = int(date_match.group(2))
            year = int(date_match.group(3) or datetime.now().year)
        else:
            month = None

    else:
        day = int(date_match.group(1))
        month = datetime.strptime(
            date_match.group(2), "%B"
        ).month
        year = int(date_match.group(3) or datetime.now().year)

    if date_match:
        try:
            target_date = date(year, month, day).isoformat()

            for name, application in application_names.items():
                if name in query:
                    return {
                        "type": "application_date",
                        "application": application,
                        "date": target_date
                    }

            return {
                "type": "date",
                "date": target_date
            }

        except ValueError:
            return {"type": "unknown"}

    # Activity for yesterday
    if "yesterday" in query:

        for name, application in application_names.items():
            if name in query:
                return {
                    "type": "application_yesterday",
                    "application": application
                }

        return {"type": "yesterday"}

    # Activity for today
    if "today" in query:

        for name, application in application_names.items():
            if name in query:
                return {
                    "type": "application_today",
                    "application": application
                }

        return {"type": "today"}

    # General application activity
    for name, application in application_names.items():

        if name in query:
            return {
                "type": "application",
                "application": application
            }

    return {"type": "unknown"}


if __name__ == "__main__":

    test_queries = [
        "What did I do on 30 October?",
        "Show my Brave activity on 30 October",
        "What was I doing on October 30?",
        "Show VS Code activity on 30 October 2026",
        "What did I do yesterday?",
        "What was I doing in Brave today?",
        "Show my activity in Brave",
        "What was my first activity?",
        "Which application did I use most?"
    ]

    for query in test_queries:
        print(f"{query} -> {parse_query(query)}")

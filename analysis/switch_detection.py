
from collections import Counter


def normalize_application(application):
    """Normalize known application names consistently."""

    if not application:
        return "Unknown"

    application_lower = application.lower()

    if "visual studio code" in application_lower:
        return "Visual Studio Code"

    if "brave" in application_lower:
        return "Brave"

    if "google chrome" in application_lower or "chrome.exe" in application_lower:
        return "Google Chrome"

    if "whatsapp" in application_lower:
        return "WhatsApp"

    if "telegram" in application_lower:
        return "Telegram"

    if "file explorer" in application_lower:
        return "File Explorer"

    if "powershell" in application_lower:
        return "PowerShell"

    if "windows terminal" in application_lower:
        return "Windows Terminal"

    return application


def find_repeated_switches(events):
    """
    Find A -> B -> A application patterns.

    Returns a list containing:
    - event_index
    - previous_application
    - current_application
    - next_application
    """

    patterns = []

    for i in range(1, len(events) - 1):

        previous_app = normalize_application(events[i - 1][1])
        current_app = normalize_application(events[i][1])
        next_app = normalize_application(events[i + 1][1])

        if (
            previous_app == next_app
            and previous_app != current_app
            and previous_app != "Unknown"
            and current_app != "Unknown"
        ):
            patterns.append({
                "event_index": i,
                "previous_application": previous_app,
                "current_application": current_app,
                "next_application": next_app
            })

    return patterns


def count_repeated_switches(events):
    """Count occurrences of each A -> B -> A pattern."""

    occurrences = find_repeated_switches(events)

    counts = Counter(
        (
            pattern["previous_application"],
            pattern["current_application"],
            pattern["next_application"]
        )
        for pattern in occurrences
    )

    return counts

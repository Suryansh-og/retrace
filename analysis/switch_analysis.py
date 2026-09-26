import sqlite3
from datetime import datetime

DATABASE_NAME = "retrace.db"


def get_events():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, application
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    return events


def normalize_application(application):

    if not application:
        return "Unknown"

    if "Visual Studio Code" in application:
        return "Visual Studio Code"

    if "Brave" in application:
        return "Brave"

    if "WhatsApp" in application:
        return "WhatsApp"

    if "Telegram" in application:
        return "Telegram"

    if "File Explorer" in application:
        return "File Explorer"

    if "PowerShell" in application:
        return "PowerShell"

    return application


events = get_events()

print("\n===== SWITCH ANALYSIS =====\n")


for i in range(1, len(events) - 1):

    previous = events[i - 1]
    current = events[i]
    next_event = events[i + 1]

    previous_app = normalize_application(previous[1])
    current_app = normalize_application(current[1])
    next_app = normalize_application(next_event[1])

    if previous_app == next_app and previous_app != current_app:

        previous_time = datetime.fromisoformat(previous[0])
        current_time = datetime.fromisoformat(current[0])
        next_time = datetime.fromisoformat(next_event[0])

        time_to_other = (
            current_time - previous_time
        ).total_seconds()

        time_to_return = (
            next_time - current_time
        ).total_seconds()

        # Ignore large gaps when the collector was not running
        if time_to_other > 60 or time_to_return > 60:
            continue

        print(
            f"🔁 {previous_app} → "
            f"{current_app} → "
            f"{next_app}"
        )

        print(
            f"   Time before switch: "
            f"{time_to_other:.1f} seconds"
        )

        print(
            f"   Time before return: "
            f"{time_to_return:.1f} seconds"
        )

        print()
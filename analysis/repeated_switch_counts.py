import sqlite3
from collections import Counter

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

patterns = Counter()

for i in range(1, len(events) - 1):

    previous_app = normalize_application(events[i - 1][1])
    current_app = normalize_application(events[i][1])
    next_app = normalize_application(events[i + 1][1])

    if previous_app == next_app and previous_app != current_app:

        pattern = (
            previous_app,
            current_app,
            next_app
        )

        patterns[pattern] += 1


print("\n===== REPEATED SWITCH COUNTS =====\n")


for pattern, count in patterns.most_common():

    print(
        f"{pattern[0]} → "
        f"{pattern[1]} → "
        f"{pattern[2]} "
        f"-> {count} times"
    )
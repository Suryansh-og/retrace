import sqlite3
from datetime import datetime
from collections import defaultdict

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


events = get_events()

usage = defaultdict(float)

for i in range(len(events) - 1):

    current = events[i]
    next_event = events[i + 1]

    current_time = datetime.fromisoformat(current[0])
    next_time = datetime.fromisoformat(next_event[0])

    duration = (next_time - current_time).total_seconds()

    # Ignore large gaps
    if duration > 60:
        continue

    application = current[1]

    if not application:
        application = "Unknown"
    # Normalize old VS Code records
    if "Visual Studio Code" in application:
        application = "Visual Studio Code"

    # Normalize old Brave records
    elif "Brave" in application:
        application = "Brave"

# Normalize old File Explorer records
    elif "File Explorer" in application:
        application = "File Explorer"

# Normalize old Telegram records
    elif "Telegram" in application:
        application = "Telegram"
    usage[application] += duration


print("\n===== USAGE SUMMARY =====\n")

for application, duration in sorted(
    usage.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(f"{application} -> {duration:.1f} seconds")
import sqlite3
from datetime import datetime

DATABASE_NAME = "retrace.db"


def get_events():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, application, context
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    return events


events = get_events()

print("\n===== APPLICATION DURATIONS =====\n")

for i in range(len(events) - 1):

    current = events[i]
    next_event = events[i + 1]

    current_time = datetime.fromisoformat(current[0])
    next_time = datetime.fromisoformat(next_event[0])

    duration = (next_time - current_time).total_seconds()

    # Ignore large gaps when the collector was probably not running
    if duration > 60:
        continue

    print(
        f"{current[1]} "
        f"-> {duration:.1f} seconds"
    )
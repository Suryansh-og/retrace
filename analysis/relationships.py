import sqlite3

DATABASE_NAME = "retrace.db"


def get_events():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, timestamp, application
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    return events


events = get_events()

print("\n===== EVENT RELATIONSHIPS =====\n")

for i in range(1, len(events)):

    previous_event = events[i - 1]
    current_event = events[i]

    print(
        f"{previous_event[2]}"
        f"  --->  "
        f"{current_event[2]}"
    )
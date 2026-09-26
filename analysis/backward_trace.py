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


def backward_trace(events, target_id, steps=5):

    target_index = None

    for i, event in enumerate(events):
        if event[0] == target_id:
            target_index = i
            break

    if target_index is None:
        print("Event not found.")
        return

    print("\n===== BACKWARD TRACE =====\n")

    start = max(0, target_index - steps)

    for i in range(target_index, start - 1, -1):

        event = events[i]

        print(
            f"{event[0]} | "
            f"{event[1]} | "
            f"{event[2]}"
        )


events = get_events()

# Trace the last recorded event
if events:
    target_id = events[-1][0]
    backward_trace(events, target_id, 5)
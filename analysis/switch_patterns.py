import sqlite3

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

print("\n===== SWITCH PATTERNS =====\n")

for i in range(len(events) - 2):

    app1 = events[i][1]
    app2 = events[i + 1][1]
    app3 = events[i + 2][1]

    if not app1:
        app1 = "Unknown"

    if not app2:
        app2 = "Unknown"

    if not app3:
        app3 = "Unknown"

    print(
        f"{app1} → {app2} → {app3}"
    )
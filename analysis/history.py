import sqlite3

DATABASE_NAME = "retrace.db"


def get_events():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            activity_type,
            context,
            task_id,
            session_id
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    return events


events = get_events()

for event in events:
    print(event)
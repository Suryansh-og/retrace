import sqlite3
from datetime import datetime

DATABASE_NAME = "retrace.db"


def get_sessions(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, start_time, end_time
        FROM sessions
        ORDER BY start_time
    """)

    return cursor.fetchall()


def assign_events_to_sessions(connection, sessions):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, timestamp
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    assigned = 0

    for event_id, timestamp in events:

        event_time = datetime.fromisoformat(timestamp)

        for session_id, start_time, end_time in sessions:

            session_start = datetime.fromisoformat(start_time)
            session_end = datetime.fromisoformat(end_time)

            if session_start <= event_time <= session_end:

                cursor.execute("""
                    UPDATE events
                    SET session_id = ?
                    WHERE id = ?
                """, (
                    session_id,
                    event_id
                ))

                assigned += 1
                break

    connection.commit()

    return assigned


connection = sqlite3.connect(DATABASE_NAME)

sessions = get_sessions(connection)

assigned = assign_events_to_sessions(
    connection,
    sessions
)

connection.close()

print("\n===== SESSION ASSIGNMENT =====\n")

print(
    f"Events assigned to sessions: {assigned}"
)

print(
    f"Total sessions: {len(sessions)}"
)
import sqlite3
from datetime import datetime

from database.database import create_database, save_session


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


def clear_existing_sessions():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    # Remove old session assignments from events
    cursor.execute("""
        UPDATE events
        SET session_id = NULL
    """)

    # Remove previously generated sessions
    cursor.execute("""
        DELETE FROM sessions
    """)

    # Reset SQLite session IDs
    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'sessions'
    """)

    connection.commit()
    connection.close()


def assign_events_to_session(event_ids, session_id):
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    for event_id in event_ids:

        cursor.execute("""
            UPDATE events
            SET session_id = ?
            WHERE id = ?
        """, (
            session_id,
            event_id
        ))

    connection.commit()
    connection.close()


def create_session(session_start, session_end, session_events):

    duration = (
        session_end - session_start
    ).total_seconds()

    event_ids = [
        event[0]
        for event in session_events
    ]

    session_id = save_session(
        session_start,
        session_end,
        duration,
        len(session_events)
    )

    assign_events_to_session(
        event_ids,
        session_id
    )

    return session_id, duration


create_database()

events = get_events()

print("\n===== RETRACE SESSIONS =====\n")


if not events:

    print("No events found.")

else:

    # Rebuild sessions from scratch
    clear_existing_sessions()

    session_number = 1

    session_start = datetime.fromisoformat(
        events[0][1]
    )

    previous_time = session_start

    session_events = [events[0]]

    for event in events[1:]:

        current_time = datetime.fromisoformat(
            event[1]
        )

        gap = (
            current_time - previous_time
        ).total_seconds()

        if gap <= 60:

            session_events.append(event)

        else:

            session_end = previous_time

            session_id, duration = create_session(
                session_start,
                session_end,
                session_events
            )

            print(
                f"Session {session_number}"
            )

            print(
                f"Start: "
                f"{session_start.strftime('%H:%M:%S')}"
            )

            print(
                f"End: "
                f"{session_end.strftime('%H:%M:%S')}"
            )

            print(
                f"Duration: "
                f"{duration:.1f} seconds"
            )

            print(
                f"Events: "
                f"{len(session_events)}"
            )

            print(
                f"Session ID: "
                f"{session_id}"
            )

            print()

            session_number += 1

            session_start = current_time

            session_events = [event]

        previous_time = current_time


    # Save final session

    session_end = previous_time

    session_id, duration = create_session(
        session_start,
        session_end,
        session_events
    )

    print(
        f"Session {session_number}"
    )

    print(
        f"Start: "
        f"{session_start.strftime('%H:%M:%S')}"
    )

    print(
        f"End: "
        f"{session_end.strftime('%H:%M:%S')}"
    )

    print(
        f"Duration: "
        f"{duration:.1f} seconds"
    )

    print(
        f"Events: "
        f"{len(session_events)}"
    )

    print(
        f"Session ID: "
        f"{session_id}"
    )
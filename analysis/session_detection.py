
import sqlite3
from datetime import datetime

from database.database import create_database, save_session


DATABASE_NAME = "retrace.db"
SESSION_GAP_SECONDS = 60


def get_events():

    connection = sqlite3.connect(DATABASE_NAME)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, timestamp, application
            FROM events
            ORDER BY timestamp
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def clear_existing_sessions():

    connection = sqlite3.connect(DATABASE_NAME)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE events
            SET session_id = NULL
        """)

        cursor.execute("""
            DELETE FROM sessions
        """)

        cursor.execute("""
            DELETE FROM sqlite_sequence
            WHERE name = 'sessions'
        """)

        connection.commit()

    finally:
        connection.close()


def assign_events_to_session(event_ids, session_id):

    connection = sqlite3.connect(DATABASE_NAME)

    try:
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

    finally:
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


def print_session(
    session_number,
    session_start,
    session_end,
    duration,
    event_count,
    session_id
):

    print(f"Session {session_number}")

    print(
        f"Start: "
        f"{session_start.strftime('%H:%M:%S')}"
    )

    print(
        f"End: "
        f"{session_end.strftime('%H:%M:%S')}"
    )

    print(f"Duration: {duration:.1f} seconds")
    print(f"Events: {event_count}")
    print(f"Session ID: {session_id}")
    print()


def main():

    create_database()

    events = get_events()

    print("\n===== RETRACE SESSIONS =====\n")

    if not events:
        print("No events found.")
        return

    # Rebuild sessions from scratch.
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

        if gap <= SESSION_GAP_SECONDS:

            session_events.append(event)

        else:

            session_end = previous_time

            session_id, duration = create_session(
                session_start,
                session_end,
                session_events
            )

            print_session(
                session_number,
                session_start,
                session_end,
                duration,
                len(session_events),
                session_id
            )

            session_number += 1

            session_start = current_time

            session_events = [event]

        previous_time = current_time

    # Save the final session.

    session_end = previous_time

    session_id, duration = create_session(
        session_start,
        session_end,
        session_events
    )

    print_session(
        session_number,
        session_start,
        session_end,
        duration,
        len(session_events),
        session_id
    )


if __name__ == "__main__":
    main()

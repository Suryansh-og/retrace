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


create_database()

events = get_events()

print("\n===== RETRACE SESSIONS =====\n")


if not events:

    print("No events found.")

else:

    session_number = 1

    session_start = datetime.fromisoformat(events[0][1])

    previous_time = session_start

    session_events = [events[0]]

    for event in events[1:]:

        current_time = datetime.fromisoformat(event[1])

        gap = (
            current_time - previous_time
        ).total_seconds()

        if gap <= 60:

            session_events.append(event)

        else:

            session_end = previous_time

            duration = (
                session_end - session_start
            ).total_seconds()

            # Save session
            save_session(
                session_start,
                session_end,
                duration,
                len(session_events)
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

            print()

            session_number += 1

            session_start = current_time

            session_events = [event]

        previous_time = current_time


    # Save final session

    session_end = previous_time

    duration = (
        session_end - session_start
    ).total_seconds()

    save_session(
        session_start,
        session_end,
        duration,
        len(session_events)
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
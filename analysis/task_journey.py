import sqlite3
from datetime import datetime

DATABASE_NAME = "retrace.db"


def get_sessions():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, start_time, end_time, duration, event_count
        FROM sessions
        ORDER BY id
    """)

    sessions = cursor.fetchall()
    connection.close()

    return sessions


def get_session_events(session_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, application, context
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp
    """, (session_id,))

    events = cursor.fetchall()
    connection.close()

    return events


def display_journey(session):
    session_id, start_time, end_time, duration, event_count = session

    events = get_session_events(session_id)

    print("\n" + "=" * 50)
    print("TASK JOURNEY")
    print("=" * 50)

    print(f"Session: {session_id}")
    print(f"Start:   {start_time}")
    print(f"End:     {end_time}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Events:   {event_count}")

    print("\nEvent Sequence:")
    print("-" * 50)

    previous_application = None
    switch_count = 0
    applications = set()

    for timestamp, application, context in events:

        time = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

        if previous_application is not None:
            print("        ↓")

            if application != previous_application:
                switch_count += 1

        print(f"{time}  {application}")

        if context:
            print(f"          {context}")

        applications.add(application)
        previous_application = application

    print("-" * 50)

    print(f"Application switches: {switch_count}")
    print(f"Unique applications: {len(applications)}")


def main():
    sessions = get_sessions()

    if not sessions:
        print("No sessions found.")
        return

    for session in sessions:
        display_journey(session)


if __name__ == "__main__":
    main()
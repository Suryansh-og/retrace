
import sqlite3
from collections import Counter
from datetime import datetime

from analysis.switch_detection import normalize_application

DATABASE_NAME = "retrace.db"
MAX_SWITCH_GAP = 60


def get_session_signals(events):

    signals = []

    for i in range(1, len(events) - 1):

        previous = events[i - 1]
        current = events[i]
        next_event = events[i + 1]

        previous_app = normalize_application(previous[1])
        current_app = normalize_application(current[1])
        next_app = normalize_application(next_event[1])

        previous_time = datetime.fromisoformat(previous[0])
        current_time = datetime.fromisoformat(current[0])
        next_time = datetime.fromisoformat(next_event[0])

        time_to_switch = (
            current_time - previous_time
        ).total_seconds()

        time_to_return = (
            next_time - current_time
        ).total_seconds()

        if (
            time_to_switch > MAX_SWITCH_GAP
            or time_to_return > MAX_SWITCH_GAP
        ):
            continue

        if (
            previous_app == next_app
            and previous_app != current_app
            and previous_app != "Unknown"
            and current_app != "Unknown"
        ):
            signals.append(
                (previous_app, current_app, next_app)
            )

    return signals


def main():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, start_time, end_time, duration, event_count
            FROM sessions
            ORDER BY id
        """)

        sessions = cursor.fetchall()

        print("\n========================================")
        print("          RETRACE SESSION REPORT")
        print("========================================")

        for session in sessions:

            session_id, start_time, end_time, duration, event_count = session

            cursor.execute("""
                SELECT timestamp, application
                FROM events
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))

            events = cursor.fetchall()

            applications = [
                normalize_application(event[1])
                for event in events
            ]

            application_counts = Counter(applications)

            switches = max(0, len(events) - 1)

            primary_application = (
                application_counts.most_common(1)[0][0]
                if application_counts
                else "Unknown"
            )

            signals = get_session_signals(events)

            print("\n----------------------------------------")
            print(f"SESSION {session_id}")

            print(
                f"Start: "
                f"{datetime.fromisoformat(start_time).strftime('%H:%M:%S')}"
            )

            print(
                f"End: "
                f"{datetime.fromisoformat(end_time).strftime('%H:%M:%S')}"
            )

            print(f"Duration: {duration:.1f} seconds")
            print(f"Events: {event_count}")
            print(f"Unique applications: {len(application_counts)}")
            print(f"Application switches: {switches}")
            print(f"Primary application: {primary_application}")

            print("\nBehavior signals:")

            if not signals:
                print("  None")

            else:
                signal_counts = Counter(signals)

                for signal, count in signal_counts.most_common():

                    print(
                        f"  {signal[0]} -> "
                        f"{signal[1]} -> "
                        f"{signal[2]} "
                        f"({count} occurrence)"
                    )

    finally:
        connection.close()


if __name__ == "__main__":
    main()


import sqlite3
from collections import Counter

from analysis.session_report import get_session_signals

DATABASE_NAME = "retrace.db"


def main():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM sessions
            ORDER BY id
        """)

        sessions = cursor.fetchall()

        print("\n========================================")
        print("       RETRACE SESSION SIGNALS")
        print("========================================")

        total_signals = 0

        for (session_id,) in sessions:

            cursor.execute("""
                SELECT timestamp, application
                FROM events
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))

            events = cursor.fetchall()

            signals = Counter(get_session_signals(events))

            print("\n----------------------------------------")
            print(f"SESSION {session_id}")

            if not signals:
                print("No repeated-switch signals.")
                continue

            session_signal_count = 0

            for pattern, count in signals.most_common():

                print(
                    f"{pattern[0]} -> "
                    f"{pattern[1]} -> "
                    f"{pattern[2]}"
                )

                print(f"   Occurrences: {count}")

                session_signal_count += count

            print(f"\nSession signals: {session_signal_count}")

            total_signals += session_signal_count

        print("\n========================================")
        print(f"Total behavioral signals: {total_signals}")
        print("========================================")

    finally:
        connection.close()


if __name__ == "__main__":
    main()

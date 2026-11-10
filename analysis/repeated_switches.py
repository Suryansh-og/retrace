
import sqlite3

from analysis.switch_detection import find_repeated_switches

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


def main():
    events = get_events()
    patterns = find_repeated_switches(events)

    print("\n===== REPEATED SWITCHES =====\n")

    for pattern in patterns:
        print(
            f"↻ {pattern['previous_application']} → "
            f"{pattern['current_application']} → "
            f"{pattern['next_application']}"
        )


if __name__ == "__main__":
    main()

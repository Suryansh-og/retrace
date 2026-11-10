
import sqlite3

from analysis.switch_detection import count_repeated_switches

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
    patterns = count_repeated_switches(events)

    print("\n===== REPEATED SWITCH COUNTS =====\n")

    for pattern, count in patterns.most_common():
        print(
            f"{pattern[0]} → "
            f"{pattern[1]} → "
            f"{pattern[2]} "
            f"-> {count} times"
        )


if __name__ == "__main__":
    main()

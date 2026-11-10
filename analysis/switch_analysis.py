
import sqlite3
from datetime import datetime

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

    print("\n===== SWITCH ANALYSIS =====\n")

    for pattern in patterns:
        i = pattern["event_index"]

        previous = events[i - 1]
        current = events[i]
        next_event = events[i + 1]

        previous_time = datetime.fromisoformat(previous[0])
        current_time = datetime.fromisoformat(current[0])
        next_time = datetime.fromisoformat(next_event[0])

        time_to_other = (
            current_time - previous_time
        ).total_seconds()

        time_to_return = (
            next_time - current_time
        ).total_seconds()

        # Ignore large gaps when the collector was not running
        if time_to_other > 60 or time_to_return > 60:
            continue

        print(
            f"↻ {pattern['previous_application']} → "
            f"{pattern['current_application']} → "
            f"{pattern['next_application']}"
        )

        print(
            f"   Time before switch: "
            f"{time_to_other:.1f} seconds"
        )

        print(
            f"   Time before return: "
            f"{time_to_return:.1f} seconds"
        )

        print()


if __name__ == "__main__":
    main()

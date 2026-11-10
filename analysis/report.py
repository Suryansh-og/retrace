
import sqlite3
from datetime import datetime
from collections import defaultdict, Counter

from analysis.switch_detection import normalize_application
from analysis.session_report import get_session_signals

DATABASE_NAME = "retrace.db"


def get_events():

    connection = sqlite3.connect(DATABASE_NAME)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT timestamp, application
            FROM events
            ORDER BY timestamp
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def main():

    events = get_events()

    # ========================================
    # TOTAL EVENTS
    # ========================================

    total_events = len(events)

    # ========================================
    # APPLICATION USAGE
    # ========================================

    usage = defaultdict(float)

    for i in range(len(events) - 1):

        current = events[i]
        next_event = events[i + 1]

        current_time = datetime.fromisoformat(current[0])
        next_time = datetime.fromisoformat(next_event[0])

        duration = (
            next_time - current_time
        ).total_seconds()

        # Ignore invalid intervals and large gaps.
        if duration <= 0 or duration > 60:
            continue

        application = normalize_application(current[1])
        usage[application] += duration

    # ========================================
    # REPORT
    # ========================================

    print("\n========================================")
    print("              RETRACE REPORT")
    print("========================================")

    print("\nEVENTS")
    print(f"Total events: {total_events}")

    print("\nAPPLICATION USAGE")

    for application, duration in sorted(
        usage.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{application:<20} "
            f"{duration:.1f} seconds"
        )

    # ========================================
    # RECENT ACTIVITY
    # ========================================

    print("\nRECENT ACTIVITY")

    recent_events = events[-10:]

    for timestamp, application in recent_events:

        time = datetime.fromisoformat(timestamp)

        application = normalize_application(application)

        print(
            f"{time.strftime('%H:%M:%S')}  "
            f"{application}"
        )

    # ========================================
    # BEHAVIOR SIGNALS
    # ========================================

    print("\nBEHAVIOR SIGNALS")

    signals = get_session_signals(events)
    patterns = Counter(signals)

    if not patterns:

        print("No behavioral signals detected.")

    else:

        total_signals = 0

        for pattern, count in patterns.most_common():

            previous_app = pattern[0]
            current_app = pattern[1]
            next_app = pattern[2]

            print(
                f"{previous_app} -> "
                f"{current_app} -> "
                f"{next_app}"
            )

            print(f"   Occurrences: {count}\n")

            total_signals += count

        print(
            f"Total repeated-switch signals: "
            f"{total_signals}"
        )


if __name__ == "__main__":
    main()

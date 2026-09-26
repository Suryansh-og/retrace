import sqlite3
from datetime import datetime
from collections import Counter

DATABASE_NAME = "retrace.db"


def normalize_application(application):

    if not application:
        return "Unknown"

    if "Visual Studio Code" in application:
        return "Visual Studio Code"

    if "Google Chrome" in application or "chrome.exe" in application:
        return "Google Chrome"

    if "Brave" in application:
        return "Brave"

    if "WhatsApp" in application:
        return "WhatsApp"

    if "Telegram" in application:
        return "Telegram"

    if "File Explorer" in application:
        return "File Explorer"

    if "PowerShell" in application:
        return "PowerShell"

    if "Windows Terminal" in application:
        return "Windows Terminal"

    return application


connection = sqlite3.connect(DATABASE_NAME)

cursor = connection.cursor()

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

    signals = Counter()

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

        # Ignore large gaps
        if time_to_switch > 60 or time_to_return > 60:
            continue

        if (
            previous_app == next_app
            and previous_app != current_app
            and previous_app != "Unknown"
            and current_app != "Unknown"
        ):

            pattern = (
                previous_app,
                current_app,
                next_app
            )

            signals[pattern] += 1


    print(f"\n----------------------------------------")
    print(f"SESSION {session_id}")

    if not signals:

        print("No repeated-switch signals.")

    else:

        session_signal_count = 0

        for pattern, count in signals.most_common():

            print(
                f"🔁 {pattern[0]} → "
                f"{pattern[1]} → "
                f"{pattern[2]}"
            )

            print(
                f"   Occurrences: {count}"
            )

            session_signal_count += count

        print(
            f"\nSession signals: "
            f"{session_signal_count}"
        )

        total_signals += session_signal_count


print("\n========================================")

print(
    f"Total behavioral signals: "
    f"{total_signals}"
)

print("========================================")


connection.close()
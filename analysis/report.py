import sqlite3
from datetime import datetime
from collections import defaultdict, Counter

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


events = get_events()

def normalize_application(application):

    if not application:
        return "Unknown"

    if "Visual Studio Code" in application:
        return "Visual Studio Code"

    if "Brave" in application:
        return "Brave"

    if "Google Chrome" in application:
        return "Google Chrome"

    if "chrome.exe" in application:
        return "Google Chrome"

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

    duration = (next_time - current_time).total_seconds()

    # Ignore invalid intervals and large gaps
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

patterns = Counter()

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

    # Ignore gaps when collector was not running
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

        patterns[pattern] += 1


if not patterns:

    print("No behavioral signals detected.")

else:

    total_signals = 0

    for pattern, count in patterns.most_common():

        previous_app = pattern[0]
        current_app = pattern[1]
        next_app = pattern[2]

        print(
            f"🔁 {previous_app} → "
            f"{current_app} → "
            f"{next_app}"
        )

        print(
            f"   Occurrences: {count}"
        )

        print()

        total_signals += count

    print(
        f"Total repeated-switch signals: "
        f"{total_signals}"
    )
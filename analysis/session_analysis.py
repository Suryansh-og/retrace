import sqlite3
from datetime import datetime
from collections import Counter

DATABASE_NAME = "retrace.db"


def normalize_application(application):

    if not application:
        return "Unknown"

    if "Visual Studio Code" in application:
        return "Visual Studio Code"

    if "Google Chrome" in application:
        return "Google Chrome"

    if "chrome.exe" in application:
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
    SELECT
        id,
        start_time,
        end_time,
        duration,
        event_count
    FROM sessions
    ORDER BY id
""")

sessions = cursor.fetchall()


print("\n========================================")
print("          RETRACE SESSION ANALYSIS")
print("========================================")


for session in sessions:

    session_id = session[0]
    start_time = session[1]
    end_time = session[2]
    duration = session[3]
    event_count = session[4]

    cursor.execute("""
        SELECT timestamp, application
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp
    """, (session_id,))

    events = cursor.fetchall()

    applications = []

    for timestamp, application in events:
        applications.append(
            normalize_application(application)
        )

    application_counts = Counter(applications)

    unique_applications = len(application_counts)

    switches = max(0, len(events) - 1)

    if application_counts:
        primary_application = (
            application_counts.most_common(1)[0][0]
        )
    else:
        primary_application = "Unknown"

    print("\n----------------------------------------")

    print(
        f"SESSION {session_id}"
    )

    print(
        f"Start: "
        f"{datetime.fromisoformat(start_time).strftime('%H:%M:%S')}"
    )

    print(
        f"End: "
        f"{datetime.fromisoformat(end_time).strftime('%H:%M:%S')}"
    )

    print(
        f"Duration: "
        f"{duration:.1f} seconds"
    )

    print(
        f"Events: "
        f"{event_count}"
    )

    print(
        f"Unique applications: "
        f"{unique_applications}"
    )

    print(
        f"Application switches: "
        f"{switches}"
    )

    print(
        f"Primary application: "
        f"{primary_application}"
    )

    print("\nApplications:")

    for application, count in application_counts.most_common():

        print(
            f"  {application} → {count}"
        )


connection.close()
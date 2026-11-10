
import sqlite3

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

    print("\n===== SWITCH PATTERNS =====\n")

    for i in range(len(events) - 2):
        app1 = events[i][1] or "Unknown"
        app2 = events[i + 1][1] or "Unknown"
        app3 = events[i + 2][1] or "Unknown"

        print(f"{app1} → {app2} → {app3}")


if __name__ == "__main__":
    main()

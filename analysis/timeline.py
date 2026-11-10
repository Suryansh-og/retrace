
import sqlite3
from datetime import datetime

DATABASE_NAME = "retrace.db"


def get_timeline():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, application, context
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()
    connection.close()

    return events


def main():
    events = get_timeline()

    print("\n===== RETRACE TIMELINE =====\n")

    for timestamp, application, context in events:
        time = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

        if not application:
            application = "Unknown"

        if not context:
            context = "No context"

        print(
            f"{time} | "
            f"{application} | "
            f"{context}"
        )


if __name__ == "__main__":
    main()

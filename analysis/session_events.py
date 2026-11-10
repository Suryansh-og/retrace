
import sqlite3

DATABASE_NAME = "retrace.db"


def get_events_per_session():

    connection = sqlite3.connect(DATABASE_NAME)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                session_id,
                COUNT(*)
            FROM events
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY session_id
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def main():

    results = get_events_per_session()

    print("\n===== EVENTS PER SESSION =====\n")

    for session_id, count in results:
        print(f"Session {session_id} -> {count} events")


if __name__ == "__main__":
    main()

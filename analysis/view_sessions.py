
import sqlite3

DATABASE_NAME = "retrace.db"


def get_sessions():

    connection = sqlite3.connect(DATABASE_NAME)

    try:
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

        return cursor.fetchall()

    finally:
        connection.close()


def main():

    sessions = get_sessions()

    print("\n===== STORED SESSIONS =====\n")

    for session in sessions:
        print(
            f"Session {session[0]} | "
            f"{session[1]} -> {session[2]} | "
            f"{session[3]:.1f}s | "
            f"{session[4]} events"
        )

    print(f"\nTotal stored sessions: {len(sessions)}")


if __name__ == "__main__":
    main()

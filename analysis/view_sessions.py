import sqlite3

DATABASE_NAME = "retrace.db"

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

connection.close()

print("\n===== STORED SESSIONS =====\n")

for session in sessions:
    print(
        f"Session {session[0]} | "
        f"{session[1]} → {session[2]} | "
        f"{session[3]:.1f}s | "
        f"{session[4]} events"
    )

print(f"\nTotal stored sessions: {len(sessions)}")
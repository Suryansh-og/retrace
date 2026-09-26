import sqlite3

DATABASE_NAME = "retrace.db"

connection = sqlite3.connect(DATABASE_NAME)

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

results = cursor.fetchall()

connection.close()

print("\n===== EVENTS PER SESSION =====\n")

for session_id, count in results:
    print(
        f"Session {session_id} → {count} events"
    )
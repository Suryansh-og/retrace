import sqlite3


DATABASE_NAME = "retrace.db"

def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            application TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            context TEXT,
            task_id INTEGER,
            session_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration REAL NOT NULL,
            event_count INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_event(event):
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO events (
            timestamp,
            application,
            activity_type,
            context,
            task_id,
            session_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event.timestamp.isoformat(),
        event.application,
        event.activity_type,
        event.context,
        event.task_id,
        event.session_id
    ))

    connection.commit()
    connection.close()

def save_session(start_time, end_time, duration, event_count):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sessions (
            start_time,
            end_time,
            duration,
            event_count
        )
        VALUES (?, ?, ?, ?)
    """, (
        start_time.isoformat(),
        end_time.isoformat(),
        duration,
        event_count
    ))

    session_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return session_id
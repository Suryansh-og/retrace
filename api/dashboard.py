from flask import Flask, jsonify, render_template
import sqlite3



app = Flask(__name__)

DATABASE_NAME = "retrace.db"
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return "Retrace Dashboard API is running."

@app.route("/api/trace/<int:event_id>")
def trace_event(event_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            context,
            session_id
        FROM events
        WHERE id = ?
    """, (event_id,))

    target = cursor.fetchone()

    if not target:
        connection.close()
        return jsonify({
            "error": "Event not found"
        }), 404

    cursor.execute("""
    SELECT
        id,
        timestamp,
        application,
        context,
        session_id
    FROM events
    WHERE id < ?
      AND session_id = ?
    ORDER BY id DESC
    LIMIT 5
""", (event_id, target["session_id"]))

    before = cursor.fetchall()

    cursor.execute("""
    SELECT
        id,
        timestamp,
        application,
        context,
        session_id
    FROM events
    WHERE id > ?
      AND session_id = ?
    ORDER BY id ASC
    LIMIT 5
""", (event_id, target["session_id"]))

    after = cursor.fetchall()

    connection.close()

    from datetime import datetime

    def format_event(event):

        return {
            "id": event["id"],
            "timestamp": datetime.fromisoformat(
                event["timestamp"]
            ).strftime("%H:%M:%S"),
            "application": event["application"] or "Unknown",
            "context": event["context"] or "",
            "session_id": event["session_id"]
        }

    return jsonify({
        "target": format_event(target),
        "before": [
            format_event(event)
            for event in reversed(before)
        ],
        "after": [
            format_event(event)
            for event in after
        ]
    })

@app.route("/api/summary")
def summary():

    connection = get_connection()
    cursor = connection.cursor()

    # Total events
    cursor.execute("""
        SELECT COUNT(*)
        FROM events
    """)
    total_events = cursor.fetchone()[0]

    # Total sessions
    cursor.execute("""
        SELECT COUNT(*)
        FROM sessions
    """)
    total_sessions = cursor.fetchone()[0]

    # Get events
    cursor.execute("""
        SELECT
            timestamp,
            application,
            session_id
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    from datetime import datetime

    def normalize_application(application):

        if not application:
            return "Unknown"

        if "Visual Studio Code" in application:
            return "Visual Studio Code"

        if "Google Chrome" in application:
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

    total_signals = 0

    for i in range(1, len(events) - 1):

        previous = events[i - 1]
        current = events[i]
        next_event = events[i + 1]

        # Signal must occur within the same session
        if (
            previous["session_id"] != current["session_id"]
            or current["session_id"] != next_event["session_id"]
        ):
            continue

        previous_app = normalize_application(
            previous["application"]
        )

        current_app = normalize_application(
            current["application"]
        )

        next_app = normalize_application(
            next_event["application"]
        )

        if (
            previous_app == "Unknown"
            or current_app == "Unknown"
            or next_app == "Unknown"
        ):
            continue

        previous_time = datetime.fromisoformat(
            previous["timestamp"]
        )

        current_time = datetime.fromisoformat(
            current["timestamp"]
        )

        next_time = datetime.fromisoformat(
            next_event["timestamp"]
        )

        time_to_switch = (
            current_time - previous_time
        ).total_seconds()

        time_to_return = (
            next_time - current_time
        ).total_seconds()

        if time_to_switch > 60 or time_to_return > 60:
            continue

        if (
            previous_app == next_app
            and previous_app != current_app
        ):
            total_signals += 1

    return jsonify({
        "total_events": total_events,
        "total_sessions": total_sessions,
        "behavior_signals": total_signals
    })

@app.route("/api/usage")
def usage():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, application
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()
    connection.close()

    from datetime import datetime

    def normalize_application(application):

        if not application:
            return "Unknown"

        if "Visual Studio Code" in application:
            return "Visual Studio Code"

        if "Google Chrome" in application:
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

    usage = {}

    for i in range(len(events) - 1):

        current_time = datetime.fromisoformat(
            events[i]["timestamp"]
        )

        next_time = datetime.fromisoformat(
            events[i + 1]["timestamp"]
        )

        duration = (
            next_time - current_time
        ).total_seconds()

        if duration > 60:
            continue

        application = normalize_application(
            events[i]["application"]
        )

        usage[application] = (
            usage.get(application, 0) + duration
        )

    result = []

    for application, duration in usage.items():

        result.append({
            "application": application,
            "duration": round(duration, 1)
        })

    result.sort(
        key=lambda x: x["duration"],
        reverse=True
    )

    return jsonify(result)

@app.route("/api/sessions")
def sessions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            start_time,
            end_time,
            duration,
            event_count
        FROM sessions
        ORDER BY id DESC
    """)

    sessions = cursor.fetchall()
    connection.close()

    result = []

    for session in sessions:
        result.append({
            "id": session["id"],
            "start_time": session["start_time"],
            "end_time": session["end_time"],
            "duration": round(session["duration"], 1),
            "event_count": session["event_count"]
        })

    return jsonify(result)

@app.route("/api/signals")
def signals():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            session_id
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()
    connection.close()

    from datetime import datetime

    def normalize_application(application):

        if not application:
            return "Unknown"

        if "Visual Studio Code" in application:
            return "Visual Studio Code"

        if "Google Chrome" in application or "chrome.exe" in application:
            return "Google Chrome"

        if "Brave" in application:
            return "Brave"

        if "WhatsApp" in application or "WhatsApp.Root.exe" in application:
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

    result = []

    for i in range(1, len(events) - 1):

        previous = events[i - 1]
        current = events[i]
        next_event = events[i + 1]

        # --------------------------------
        # Same-session requirement
        # --------------------------------

        if (
            previous["session_id"] != current["session_id"]
            or current["session_id"] != next_event["session_id"]
        ):
            continue

        previous_app = normalize_application(
            previous["application"]
        )

        current_app = normalize_application(
            current["application"]
        )

        next_app = normalize_application(
            next_event["application"]
        )

        previous_time = datetime.fromisoformat(
            previous["timestamp"]
        )

        current_time = datetime.fromisoformat(
            current["timestamp"]
        )

        next_time = datetime.fromisoformat(
            next_event["timestamp"]
        )

        time_to_switch = (
            current_time - previous_time
        ).total_seconds()

        time_to_return = (
            next_time - current_time
        ).total_seconds()

        # --------------------------------
        # Ignore large gaps
        # --------------------------------

        if time_to_switch > 60 or time_to_return > 60:
            continue

        # --------------------------------
        # Ignore unknown applications
        # --------------------------------

        if (
            previous_app == "Unknown"
            or current_app == "Unknown"
            or next_app == "Unknown"
        ):
            continue

        # --------------------------------
        # Detect A → B → A
        # --------------------------------

        if (
            previous_app == next_app
            and previous_app != current_app
        ):

            result.append({
                "event_id": current["id"],

                "session_id": current["session_id"],

                "pattern": (
                    f"{previous_app} → "
                    f"{current_app} → "
                    f"{next_app}"
                ),

                "timestamp": current["timestamp"],

                "time_before_switch": round(
                    time_to_switch, 1
                ),

                "time_before_return": round(
                    time_to_return, 1
                )
            })

    return jsonify(result)

@app.route("/api/timeline")
def timeline():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            context,
            session_id
        FROM events
        ORDER BY timestamp DESC
        LIMIT 30
    """)

    events = cursor.fetchall()
    connection.close()

    from datetime import datetime

    def normalize_application(application):

        if not application:
            return "Unknown"

        if "Visual Studio Code" in application:
            return "Visual Studio Code"

        if "Google Chrome" in application or "chrome.exe" in application:
            return "Google Chrome"

        if "Brave" in application:
            return "Brave"

        if "WhatsApp" in application or "WhatsApp.Root.exe" in application:
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

    result = []

    for event in events:

        result.append({
            "id": event["id"],
            "timestamp": datetime.fromisoformat(
                event["timestamp"]
            ).strftime("%H:%M:%S"),
            "application": normalize_application(
                event["application"]
            ),
            "context": event["context"] or "",
            "session_id": event["session_id"]
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
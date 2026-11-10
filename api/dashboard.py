from flask import Flask, jsonify, render_template
from database.database import create_database
import sqlite3

from models.application import normalize_application
from collector.controller import (
    start_collector,
    stop_collector,
    get_collector_status
)

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend",
    static_url_path=""
)

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

    # Find events before the target.
    # If session_id is NULL, fall back to nearby event IDs.
    if target["session_id"] is None:
        cursor.execute("""
            SELECT
                id,
                timestamp,
                application,
                context,
                session_id
            FROM events
            WHERE id < ?
            ORDER BY id DESC
            LIMIT 5
        """, (event_id,))
    else:
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

    # Find events after the target.
    if target["session_id"] is None:
        cursor.execute("""
            SELECT
                id,
                timestamp,
                application,
                context,
                session_id
            FROM events
            WHERE id > ?
            ORDER BY id ASC
            LIMIT 5
        """, (event_id,))
    else:
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
            "timestamp": event["timestamp"],
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


    signal_patterns = set()

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

        if time_to_return < 3:
            continue

        if (
            previous_app == next_app
            and previous_app != current_app
        ):

            pattern = (
                current["session_id"],
                previous_app,
                current_app
            )

            signal_patterns.add(pattern)

    total_signals = len(signal_patterns)

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
    from collections import defaultdict

    def normalize_application(application):

        if not application:
            return "Unknown"

        if "Visual Studio Code" in application:
            return "Visual Studio Code"

        if "Google Chrome" in application or "chrome.exe" in application:
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


    # --------------------------------
    # Find individual A → B → A events
    # --------------------------------

    grouped = defaultdict(list)

    for i in range(1, len(events) - 1):

        previous = events[i - 1]
        current = events[i]
        next_event = events[i + 1]

        # Same session
        if (
            previous["session_id"] != current["session_id"]
            or current["session_id"] != next_event["session_id"]
        ):
            continue

        previous_app = normalize_application(previous["application"])
        current_app = normalize_application(current["application"])
        next_app = normalize_application(next_event["application"])

        # Ignore unknown applications
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

        # Ignore large gaps
        if time_to_switch > 60 or time_to_return > 60:
            continue

        # Ignore extremely fast switches
        if time_to_return < 3:
            continue

        # A → B → A
        if (
            previous_app == next_app
            and previous_app != current_app
        ):

            key = (
                current["session_id"],
                previous_app,
                current_app
            )

            grouped[key].append({
                "event_id": current["id"],
                "timestamp": current["timestamp"],
                "time_before_switch": round(
                    time_to_switch, 1
                ),
                "time_before_return": round(
                    time_to_return, 1
                )
            })


    # --------------------------------
    # Convert groups into signals
    # --------------------------------

    result = []

    for key, occurrences in grouped.items():

        session_id, previous_app, current_app = key

        # Use the first occurrence for Trace Back
        first_occurrence = occurrences[0]

        result.append({
            "event_id": first_occurrence["event_id"],

            "session_id": session_id,

            "pattern": (
                f"{previous_app} → "
                f"{current_app} → "
                f"{previous_app}"
            ),

            "timestamp": first_occurrence["timestamp"],

            "count": len(occurrences),

            "time_before_switch": (
                first_occurrence["time_before_switch"]
            ),

            "time_before_return": (
                first_occurrence["time_before_return"]
            )
        })


    # Stronger/repeated patterns first
    result.sort(
        key=lambda signal: signal["count"],
        reverse=True
    )

    return jsonify(result)

@app.route("/api/relationships")
def relationships():

    from analysis.relationships import find_relationships

    result = find_relationships()

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
            activity_type,
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
            "timestamp": event["timestamp"],
            "application": normalize_application(
                event["application"]
            ),
            "activity_type": event["activity_type"],
            "context": event["context"] or "",
            "session_id": event["session_id"]
        })

    return jsonify(result)

@app.route("/api/sessions/<int:session_id>/events")
def session_events(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            activity_type,
            context,
            session_id
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))

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

    result = []

    for event in events:

        result.append({
            "id": event["id"],
            "timestamp": event["timestamp"],
            "application": normalize_application(
                event["application"]
            ),
            "activity_type": event["activity_type"],
            "context": event["context"] or "",
            "session_id": event["session_id"]
        })

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
        ORDER BY start_time DESC
    """)

    sessions = cursor.fetchall()

    connection.close()

    result = []

    for session in sessions:

        result.append({
            "id": session["id"],
            "start_time": session["start_time"],
            "end_time": session["end_time"],
            "duration": session["duration"],
            "event_count": session["event_count"]
        })

    return jsonify(result)


@app.route("/api/sessions/<int:session_id>")
def session_details(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            activity_type,
            context,
            session_id
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp
    """, (session_id,))

    events = cursor.fetchall()

    connection.close()

    result = []

    for event in events:

        result.append({
            "id": event["id"],
            "timestamp": event["timestamp"],
            "application": event["application"],
            "activity_type": event["activity_type"],
            "context": event["context"] or "",
            "session_id": event["session_id"]
        })

    return jsonify(result)

@app.route("/api/query/natural")
def natural_query():

    from flask import request

    query = request.args.get("query")

    if not query:
        return jsonify({
            "error": "Missing query"
        }), 400

    from analysis.query_parser import parse_query

    parsed = parse_query(query)

    if parsed["type"] == "unknown":
        return jsonify({
            "error": "I could not understand that query."
        }), 400

    query_type = parsed["type"]

    # Application-related queries
    if query_type in [
        "application",
        "before_application",
        "after_application",
        "application_today",
        "application_yesterday",
        "application_date"
    ]:
        value = parsed.get("application")

    # Event-related queries
    elif query_type in ["before", "after", "context"]:
        value = parsed.get("event_id")

    # Session queries
    elif query_type == "session":
        value = parsed.get("session_id")

    else:
        value = ""

    response = {
        "query_type": query_type,
        "value": value
    }

    # Attach specific date when applicable
    if query_type in ["date", "application_date"]:
        response["date"] = parsed.get("date")

    return jsonify(response)

@app.route("/api/query")
def query():

    from flask import request

    query_type = request.args.get("type")
    value = request.args.get("value")
    target_date = request.args.get("date")

    limit = request.args.get(
        "limit",
        default=5,
        type=int
    )

    if limit < 1:
        return jsonify({
            "error": "Limit must be at least 1"
        }), 400

    if limit > 100:
        limit = 100

    from analysis.query_engine import (
        find_by_application,
        find_by_session,
        find_by_time_range,
        find_before_event,
        find_after_event,
        find_before_application,
        find_after_application,
        get_event_context,
        get_latest_event,
        get_earliest_event,
        find_today,
        find_by_application_today,
        find_sessions_today,
        find_yesterday,
        find_by_application_yesterday,
        get_recent_events,
        find_by_date,
        find_by_application_date
    )

    if not query_type:
        return jsonify({
            "error": "Missing query type"
        }), 400

    if query_type not in [
        "time",
        "latest",
        "earliest",
        "today",
        "yesterday",
        "date",
        "session_today",
        "recent",
        "most_used"
    ] and not value:
        return jsonify({
            "error": "Missing query value"
        }), 400

    if query_type == "most_used":

        usage_response = usage()
        usage_data = usage_response.get_json()

        return jsonify({
            "query_type": "most_used",
            "count": len(usage_data),
            "results": usage_data
        })

    if query_type == "application":

        results = find_by_application(value)

    elif query_type == "session":

        try:
            session_id = int(value)
        except ValueError:
            return jsonify({
                "error": "Session ID must be a number"
            }), 400

        results = find_by_session(session_id)

    elif query_type == "time":

        start_time = request.args.get("start")
        end_time = request.args.get("end")

        if not start_time or not end_time:
            return jsonify({
                "error": "Start and end time are required"
            }), 400

        results = find_by_time_range(
            start_time,
            end_time
        )

    elif query_type == "before":

        try:
            event_id = int(value)
        except ValueError:
            return jsonify({
                "error": "Event ID must be a number"
            }), 400

        results = find_before_event(event_id, limit)

    elif query_type == "after":

        try:
            event_id = int(value)
        except ValueError:
            return jsonify({
                "error": "Event ID must be a number"
            }), 400

        results = find_after_event(event_id, limit)

    elif query_type == "before_application":

        results = find_before_application(value, limit)

    elif query_type == "after_application":

        results = find_after_application(value, limit)

    elif query_type == "context":

        try:
            event_id = int(value)
        except ValueError:
            return jsonify({
                "error": "Event ID must be a number"
            }), 400

        context = get_event_context(event_id)

        def format_event(event):

            return {
                "id": event[0],
                "timestamp": event[1],
                "application": event[2],
                "activity_type": event[3],
                "context": event[4],
                "task_id": event[5],
                "session_id": event[6]
            }


        return jsonify({
            "query_type": query_type,
            "value": event_id,

            "before": [
                format_event(event)
                for event in context["before"]
            ],

            "target": (
                format_event(context["target"])
                if context["target"]
                else None
            ),

            "after": [
                format_event(event)
                for event in context["after"]
            ]
        })

    elif query_type == "latest":

        event = get_latest_event()

        if event is None:
            return jsonify({
                "query_type": "latest",
                "result": None
            })

        return jsonify({
            "query_type": "latest",
            "result": {
                "id": event[0],
                "timestamp": event[1],
                "application": event[2],
                "activity_type": event[3],
                "context": event[4],
                "task_id": event[5],
                "session_id": event[6]
            }
        })                    

    elif query_type == "earliest":

        event = get_earliest_event()

        if event is None:
            return jsonify({
                "query_type": "earliest",
                "result": None
            })

        return jsonify({
            "query_type": "earliest",
            "result": {
                "id": event[0],
                "timestamp": event[1],
                "application": event[2],
                "activity_type": event[3],
                "context": event[4],
                "task_id": event[5],
                "session_id": event[6]
            }
        })

    elif query_type == "today":

        results = find_today()

    elif query_type == "application_today":

        results = find_by_application_today(value)

    elif query_type == "yesterday":

        results = find_yesterday()

    elif query_type == "application_yesterday":

        results = find_by_application_yesterday(value)

    elif query_type == "date":

        if not target_date:
            return jsonify({
                "error": "Date is required"
            }), 400

        try:
            results = find_by_date(target_date)

        except ValueError:
            return jsonify({
                "error": "Invalid date format. Use YYYY-MM-DD."
            }), 400

    elif query_type == "application_date":

        if not target_date:
            return jsonify({
                "error": "Date is required"
            }), 400

        try:
            results = find_by_application_date(
                value,
                target_date
            )

        except ValueError:
            return jsonify({
                "error": "Invalid date format. Use YYYY-MM-DD."
            }), 400

    elif query_type == "session_today":

        sessions = find_sessions_today()

        return jsonify({
            "query_type": query_type,
            "count": len(sessions),
            "sessions": sessions
        })

    elif query_type == "recent":

        limit = request.args.get(
            "limit",
            default=10,
            type=int
        )

        if limit < 1:
            return jsonify({
                "error": "Limit must be at least 1"
            }), 400

        if limit > 100:
            limit = 100

        results = get_recent_events(limit)
    
    else:

        return jsonify({
            "error": "Unsupported query type"
        }), 400

    response = {
        "query_type": query_type,
        "value": value,
        "count": len(results),
        "results": [
            {
                "id": event[0],
                "timestamp": event[1],
                "application": event[2],
                "activity_type": event[3],
                "context": event[4],
                "task_id": event[5],
                "session_id": event[6]
            }
            for event in results
        ]
    }

    if query_type in ["date", "application_date"]:
        response["date"] = target_date

    return jsonify(response)

@app.route("/api/collector/start", methods=["POST"])
def start_activity_collection():
    result = start_collector()

    status_code = 409 if result["status"] == "running" and (
        result["message"] == "Activity collection is already running."
    ) else 200

    return jsonify(result), status_code


@app.route("/api/collector/stop", methods=["POST"])
def stop_activity_collection():
    result = stop_collector()

    status_code = 202 if result["status"] == "stopping" else 200

    return jsonify(result), status_code


@app.route("/api/collector/status", methods=["GET"])
def activity_collection_status():
    return jsonify({
        "status": get_collector_status()
    })


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
import sqlite3

DATABASE_NAME = "retrace.db"

def get_events():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            application,
            activity_type,
            context,
            task_id,
            session_id
        FROM events
        ORDER BY timestamp
    """)

    events = cursor.fetchall()

    connection.close()

    return events

def get_latest_event():

    events = get_events()

    if not events:
        return None

    return events[-1]

def get_earliest_event():

    events = get_events()

    if not events:
        return None

    return events[0]

from datetime import datetime


def find_today():

    events = get_events()

    today = datetime.now().date()

    results = []

    for event in events:

        timestamp = datetime.fromisoformat(event[1])

        if timestamp.date() == today:
            results.append(event)

    return results

def find_by_application(application):

    events = get_events()

    results = []

    for event in events:

        if event[2].lower() == application.lower():
            results.append(event)

    return results

def find_by_time_range(start_time, end_time):

    events = get_events()

    results = []

    for event in events:

        timestamp = event[1]

        if start_time <= timestamp <= end_time:
            results.append(event)

    return results

def find_by_session(session_id):

    events = get_events()

    results = []

    for event in events:

        if event[6] == session_id:
            results.append(event)

    return results

def find_before_event(event_id, limit=5):

    events = get_events()

    target_index = None

    for i, event in enumerate(events):

        if event[0] == event_id:
            target_index = i
            break

    if target_index is None:
        return []

    start_index = max(0, target_index - limit)

    return events[start_index:target_index]

def find_after_event(event_id, limit=5):

    events = get_events()

    target_index = None

    for i, event in enumerate(events):

        if event[0] == event_id:
            target_index = i
            break

    if target_index is None:
        return []

    end_index = target_index + 1 + limit

    return events[target_index + 1:end_index]

def find_before_application(application, limit=5):

    events = sorted(get_events(), key=lambda event: event[0])

    application = application.lower()

    # Find the latest transition INTO this application
    opening_index = None

    for i in range(1, len(events)):

        current = events[i]
        previous = events[i - 1]

        if (
            current[2].lower() == application
            and previous[2].lower() != application
        ):
            opening_index = i

    if opening_index is None:
        return []

    # Find the beginning of the previous application sequence
    previous_index = opening_index - 1
    previous_application = events[previous_index][2].lower()

    start = previous_index

    while start > 0:
        if events[start - 1][2].lower() != previous_application:
            break
        start -= 1

    return events[start:opening_index]

def get_event_context(event_id, before=5, after=5):

    events = get_events()

    target_event = None

    for event in events:

        if event[0] == event_id:
            target_event = event
            break

    if target_event is None:
        return {
            "before": [],
            "target": None,
            "after": []
        }

    events_before = find_before_event(
        event_id,
        before
    )

    events_after = find_after_event(
        event_id,
        after
    )

    return {
        "before": events_before,
        "target": target_event,
        "after": events_after
    }

def find_after_application(application, limit=5):

    print("NEW FUNCTION CALLED:", application)

    events = get_events()

    matching_events = []

    for event in events:

        if (
            event[2].lower() == application.lower()
            and event[3] == "application_switch"
        ):
            matching_events.append(event)

    if not matching_events:
        return []

    target_event = matching_events[-1]

    return find_after_event(
        target_event[0],
        limit
    )

def find_by_application_today(application):

    events = find_today()

    results = []

    for event in events:

        if event[2].lower() == application.lower():
            results.append(event)

    return results

def find_sessions_today():

    events = find_today()

    sessions = []

    for event in events:

        session_id = event[6]

        if session_id is not None and session_id not in sessions:
            sessions.append(session_id)

    return sessions

def get_recent_events(limit=10):

    events = get_events()

    if not events:
        return []

    return events[-limit:]

if __name__ == "__main__":

    context = get_event_context(
        251,
        before=5,
        after=5
    )

    print("\n===== EVENT CONTEXT =====\n")

    print("BEFORE:")

    for event in context["before"]:

        print(
            f"Event {event[0]} | "
            f"{event[2]} | "
            f"{event[4]}"
        )

    print("\nTARGET:")

    print("Event 251 | Visual Studio Code | File: application.py")

    print("\nAFTER:")

    for event in context["after"]:

        print(
            f"Event {event[0]} | "
            f"{event[2]} | "
            f"{event[4]}"
        )
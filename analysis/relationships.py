import sqlite3
from datetime import datetime

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


def find_relationships():

    events = get_events()

    relationships = []

    for i in range(1, len(events)):

        previous = events[i - 1]
        current = events[i]

        previous_id = previous[0]
        previous_time = datetime.fromisoformat(previous[1])
        previous_app = previous[2]
        previous_session = previous[6]

        current_id = current[0]
        current_time = datetime.fromisoformat(current[1])
        current_app = current[2]
        current_session = current[6]

        time_gap = (
            current_time - previous_time
        ).total_seconds()
        # Ignore relationships across large time gaps
        if time_gap > 60:
            continue

        # Same session relationship
        if (
            previous_session is not None
            and previous_session == current_session
        ):

            relationships.append({
                "from_event": previous_id,
                "to_event": current_id,
                "type": "same_session",
                "time_gap": round(time_gap, 1)
            })

        # Application switch relationship
        if previous_app != current_app:

            relationships.append({
                "from_event": previous_id,
                "to_event": current_id,
                "type": "application_switch",
                "time_gap": round(time_gap, 1)
            })


        # Same application relationship
        if previous_app == current_app:

            relationships.append({
                "from_event": previous_id,
                "to_event": current_id,
                "type": "same_application",
                "time_gap": round(time_gap, 1)
            })

    return relationships


if __name__ == "__main__":

    print("\n===== RETRACE EVENT RELATIONSHIPS =====\n")

    relationships = find_relationships()

    for relationship in relationships:

        print(
            f"Event {relationship['from_event']} "
            f"→ Event {relationship['to_event']} | "
            f"{relationship['type']} | "
            f"{relationship['time_gap']}s"
        )

    print(
        f"\nTotal relationships: "
        f"{len(relationships)}"
    )
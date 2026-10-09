from analysis.query_parser import parse_query
from analysis.query_engine import (
    find_before_event,
    find_after_event
)


def run_query(query):

    parsed = parse_query(query)

    query_type = parsed["type"]

    if query_type == "before":

        return find_before_event(
            parsed["event_id"]
        )

    if query_type == "after":

        return find_after_event(
            parsed["event_id"]
        )

    if query_type == "latest":

        from analysis.query_engine import get_latest_event

        return get_latest_event()

    if query_type == "earliest":

        from analysis.query_engine import get_earliest_event

        return get_earliest_event()

    if query_type == "recent":

        from analysis.query_engine import get_recent_events

        return get_recent_events(
            parsed.get("limit", 10)
        )

    if query_type == "today":

        from analysis.query_engine import find_today

        return find_today()

    if query_type == "application_today":

        from analysis.query_engine import find_by_application_today

        return find_by_application_today(
            parsed["application"]
        )

    if query_type == "session":

        from analysis.query_engine import find_by_session

        return find_by_session(
            parsed["session_id"]
        )

    if query_type == "before_application":

        from analysis.query_engine import find_before_application

        return find_before_application(
            parsed["application"]
        )

    if query_type == "after_application":

        from analysis.query_engine import find_after_application

        return find_after_application(
            parsed["application"]
        )
    
    if query_type == "context":

        from analysis.query_engine import get_event_context

        return get_event_context(
            parsed["event_id"]
        )

    return {
        "error": "Query type not implemented yet"
    }


if __name__ == "__main__":

    queries = [
    "What is my latest activity?",
    "What was my first activity?",
    "Show my last activities",
    "What was I doing today?",
    "What was I doing in VS Code today?",
    "Show me session 31",
    "What happened before event 251?",
    "What happened after event 251?",
    "What was I doing before opening Brave?",
    "What did I do after opening VS Code?",
    "What happened around event 251?"
    ]

    for query in queries:

        print("\nQuery:", query)

        result = run_query(query)

        print("Result:")

        if isinstance(result, dict):

            print("\nBEFORE:")

            for event in result["before"]:
                print(event)

            print("\nTARGET:")

            print(result["target"])

            print("\nAFTER:")

            for event in result["after"]:
                print(event)

        else:

            for event in result:
                print(event)
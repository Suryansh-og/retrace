from datetime import datetime


class Event:
    def __init__(
        self,
        application,
        activity_type,
        context=None,
        task_id=None,
        session_id=None
    ):
        self.id = None
        self.timestamp = datetime.now()
        self.application = application
        self.activity_type = activity_type
        self.context = context
        self.task_id = task_id
        self.session_id = session_id

    def __str__(self):
        return (
            f"Event("
            f"time={self.timestamp}, "
            f"application={self.application}, "
            f"type={self.activity_type}, "
            f"context={self.context})"
        )
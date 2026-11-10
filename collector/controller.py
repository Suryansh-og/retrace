import threading

from collector.activity_collector import collect_activity, stop_event


_collector_thread = None
_controller_lock = threading.Lock()


def start_collector():
    global _collector_thread

    with _controller_lock:

        if _collector_thread is not None and _collector_thread.is_alive():
            return {
                "status": "running",
                "message": "Activity collection is already running."
            }

        stop_event.clear()

        _collector_thread = threading.Thread(
            target=collect_activity,
            name="RetraceCollector",
            daemon=True
        )

        _collector_thread.start()

        return {
            "status": "running",
            "message": "Activity collection started."
        }


def stop_collector():
    global _collector_thread

    with _controller_lock:

        if _collector_thread is None or not _collector_thread.is_alive():
            _collector_thread = None

            return {
                "status": "stopped",
                "message": "Activity collection is not running."
            }

        stop_event.set()
        thread = _collector_thread

    # Wait outside the lock so the collector can finish.
    thread.join(timeout=5)

    with _controller_lock:

        if thread.is_alive():
            return {
                "status": "stopping",
                "message": "Activity collection has not stopped yet."
            }

        if _collector_thread is thread:
            _collector_thread = None

        return {
            "status": "stopped",
            "message": "Activity collection stopped."
        }


def get_collector_status():

    with _controller_lock:

        if _collector_thread is not None and _collector_thread.is_alive():
            return "running"

        return "stopped"
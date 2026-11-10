
import win32gui
import win32process
import psutil
import time
import threading

from models.application import (
    normalize_application,
    parse_vscode_title,
    parse_file_explorer_title,
    clean_brave_title
)

from models.event import Event
from database.database import create_database, save_event


def get_active_window():

    window = win32gui.GetForegroundWindow()

    title = win32gui.GetWindowText(window)

    try:
        _, process_id = win32process.GetWindowThreadProcessId(window)

        process = psutil.Process(process_id)

        process_name = process.name()

    except (psutil.NoSuchProcess, psutil.AccessDenied):

        process_name = "Unknown"

    return process_name, title


stop_event = threading.Event()


def collect_activity():

    last_window = None
    last_context = None

    create_database()

    while not stop_event.is_set():

        process_name, title = get_active_window()

        application = normalize_application(process_name)

        # Ignore completely unidentified windows
        if application == "Unknown" and not title:

            last_window = application
            last_context = title

            stop_event.wait(1)
            continue

        # Normalize application context
        context = title

        # Clean Brave browser title
        if application == "Brave":

            brave_title = clean_brave_title(title)

            if brave_title:
                context = brave_title

        # Extract VS Code file and project
        elif application == "Visual Studio Code":

            vscode_info = parse_vscode_title(title)

            if vscode_info:
                context = (
                    f"File: {vscode_info['file']} | "
                    f"Project: {vscode_info['project']}"
                )

        # Extract File Explorer folder
        elif application == "File Explorer":

            folder = parse_file_explorer_title(title)

            if folder:
                context = f"Folder: {folder}"

        # Detect meaningful changes
        application_changed = application != last_window
        context_changed = context != last_context

        if application_changed or context_changed:

            # Determine activity type
            if application_changed:

                activity_type = "application_switch"

            elif application == "Visual Studio Code":

                activity_type = "file_change"

            elif application == "File Explorer":

                activity_type = "folder_change"

            else:

                activity_type = "window_change"

            event = Event(
                application=application,
                activity_type=activity_type,
                context=context
            )

            save_event(event)

            print(event)

            last_window = application
            last_context = context

        stop_event.wait(1)


if __name__ == "__main__":

    try:
        collect_activity()

    except KeyboardInterrupt:

        stop_event.set()

        print("\nActivity collection stopped.")

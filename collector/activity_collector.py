import win32gui
import win32process
import psutil
import time

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


last_window = None
last_title = None
create_database()


while True:

    process_name, title = get_active_window()

    application = normalize_application(process_name)

    current_window = application

    if (
    current_window != last_window
    or title != last_title
    ):

        # Ignore completely unidentified windows
        if application == "Unknown" and not title:

            last_window = current_window

            time.sleep(1)

            continue

        context = title
        context = title

        # Clean Brave browser title
        if application == "Brave":

            brave_title = clean_brave_title(title)

            if brave_title:
                context = brave_title

        # Extract VS Code file and project
        if application == "Visual Studio Code":

            vscode_info = parse_vscode_title(title)

            if vscode_info:

                context = (
                    f"File: {vscode_info['file']} | "
                    f"Project: {vscode_info['project']}"
                )

        # Extract File Explorer folder
        if application == "File Explorer":

            folder = parse_file_explorer_title(title)

            if folder:

                context = f"Folder: {folder}"

        activity_type = "application_switch"

        if application == last_window:
            if application == "Visual Studio Code":
                activity_type = "file_change"

            elif application == "File Explorer":
                activity_type = "folder_change"


        event = Event(
            application=application,
            activity_type=activity_type,
            context=context
        )

        save_event(event)

        print(event)

        last_window = current_window
        last_title = title
    time.sleep(1)
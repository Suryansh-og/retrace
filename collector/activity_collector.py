import win32gui
import win32process
import psutil
import time

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


def get_application_name(process_name):

    applications = {

        "Code.exe": "Visual Studio Code",
        "brave.exe": "Brave",
        "WhatsApp.exe": "WhatsApp",
        "WhatsApp.Root.exe": "WhatsApp",
        "Telegram.exe": "Telegram",
        "explorer.exe": "File Explorer",
        "powershell.exe": "PowerShell",
        "WindowsTerminal.exe": "Windows Terminal",
        "chrome.exe": "Google Chrome",

    }

    return applications.get(
        process_name,
        process_name
    )


last_window = None

create_database()


while True:

    process_name, title = get_active_window()

    application = get_application_name(process_name)

    current_window = application

    if current_window != last_window:
        # Ignore completely unidentified windows
        if application == "Unknown" and not title:
            last_window = current_window
            time.sleep(1)
            continue
        event = Event(
            application=application,
            activity_type="application_switch",
            context=title
        )

        save_event(event)

        print(event)

        last_window = current_window

    time.sleep(1) 
APPLICATION_NAMES = {
    "Code.exe": "Visual Studio Code",
    "chrome.exe": "Google Chrome",
    "brave.exe": "Brave",
    "Brave": "Brave",
    "WhatsApp.exe": "WhatsApp",
    "WhatsApp.Root.exe": "WhatsApp",
    "Telegram.exe": "Telegram",
    "explorer.exe": "File Explorer",
    "powershell.exe": "PowerShell",
    "WindowsTerminal.exe": "Windows Terminal",
}


def normalize_application(process_name):
    return APPLICATION_NAMES.get(process_name, process_name)


def parse_vscode_title(title):
    """
    Extract the active file and project name
    from a VS Code window title.

    Example:
        dashboard.py - retrace - Visual Studio Code

    Returns:
        {
            "file": "dashboard.py",
            "project": "retrace"
        }
    """

    if not title:
        return None

    marker = " - Visual Studio Code"

    if marker not in title:
        return None

    clean_title = title.replace(marker, "").strip()

    parts = clean_title.split(" - ")

    if len(parts) < 2:
        return None

    return {
        "file": parts[0].strip(),
        "project": parts[1].strip()
    }

def clean_brave_title(title):
    """
    Clean Brave browser window titles.

    Examples:
        "(179) YouTube - Brave" -> "YouTube"
        "YouTube - Brave" -> "YouTube"
        "Add Binary - LeetCode - Brave" -> "Add Binary - LeetCode"
    """

    if not title:
        return None

    # Remove Brave suffix
    title = title.replace(" - Brave", "").strip()

    # Remove notification/count prefix such as "(179)"
    if title.startswith("("):
        closing = title.find(")")

        if closing != -1:
            title = title[closing + 1:].strip()

    return title

def parse_file_explorer_title(title):
    """
    Extract the currently visible folder name
    from a File Explorer window title.

    Example:
        Folder: api

    or:
        api - File Explorer
    """

    if not title:
        return None

    # Our current Windows setup may provide:
    # "Folder: api"
    if title.startswith("Folder:"):
        folder = title.replace("Folder:", "", 1).strip()

        if folder:
            return folder

    # Standard Explorer title format
    marker = " - File Explorer"

    if marker in title:
        folder = title.replace(marker, "", 1).strip()

        if folder:
            return folder

    return None
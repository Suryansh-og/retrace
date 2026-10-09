# Retrace — Digital Behavior Intelligence

Retrace is a privacy-first Windows desktop activity analysis system that records foreground application activity and analyzes patterns in digital behavior.

It helps explore application usage, application switching, session activity, and relationships between events to investigate potential interruptions and distraction patterns.

> **Project status:** Mini project — Level 1 pipeline implemented.

## Features

- **Activity Collection:** Collects Windows foreground application activity.
- **Activity History:** Stores collected events in SQLite.
- **Session Detection:** Groups activity into sessions for analysis.
- **Application Usage Analysis:** Examines time spent across applications.
- **Application Switching Analysis:** Analyzes transitions between applications.
- **Behavior Signals:** Identifies repeated application-switching patterns.
- **Event Relationships:** Displays relationships between recorded events.
- **Backward Tracing:** Allows exploration of events before and after a target event.
- **Interactive Dashboard:** Presents activity history and analysis through a Flask web application.
- **Ask Retrace:** Provides an interface for querying activity information.

## How It Works

Retrace follows this pipeline:

**Activity Collection → History Storage → Timeline → Event Relationships → Backward Tracing → Pattern Analysis → Dashboard**

1. The collector records foreground application activity.
2. Events are stored in a local SQLite database.
3. Analysis modules process activity history and detect sessions.
4. Event relationships and application-switching patterns are examined.
5. Backward tracing helps investigate the context surrounding a selected event.
6. The dashboard presents the resulting activity history and analysis.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Web framework | Flask |
| Database | SQLite |
| Windows activity collection | pywin32 |
| Process information | psutil |
| Frontend | HTML, CSS, JavaScript |

## Project Structure

```text
retrace/
├── collector/    # Activity collection
├── database/     # Database functionality
├── models/       # Data models
├── analysis/     # Session and behavior analysis
├── api/          # Flask application and API
├── frontend/     # Dashboard interface
├── .gitignore
└── README.md
```

## Current Scope

The current version focuses on collecting and analyzing desktop activity, exploring event relationships, and presenting results in a dashboard.

Retrace's analysis should be treated as **behavioral signals, not proof of distraction or task abandonment**. These patterns require context and should not be interpreted as definitive conclusions about a person's intent.

## Privacy

Retrace is designed around desktop activity history. Before using it, review what information is collected, where it is stored, and how long it is retained. Avoid collecting or publishing personal activity data without appropriate consent.

## Future Improvements

Potential areas for development include:

- More robust event relationship analysis
- Improved explanations of detected behavior patterns
- Reproducible automated tests
- Better documentation and demo materials
- Additional privacy controls and data-management options

## Author

Developed as a software engineering mini project.
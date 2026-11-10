# Retrace — Digital Activity Intelligence

**Understand your digital activity. Reconstruct your workflow. Discover patterns behind your screen time.**

Retrace is a privacy-focused Windows desktop activity analysis system that transforms foreground application activity into structured, searchable and interpretable activity history.

It records application activity locally, identifies work sessions, analyzes application usage and switching patterns, explores relationships between events, and helps users investigate their past digital activity through an interactive dashboard.

Rather than simply displaying screen time, Retrace aims to provide context about how activity unfolds across applications and sessions.

---

## Overview

Modern desktop workflows involve constantly switching between applications, tasks and windows. Understanding what happened during a particular period can be difficult when activity is spread across multiple applications.

Retrace addresses this by organizing desktop activity into an analyzable timeline.

Its processing pipeline combines:

- Foreground application activity collection.
- Local event storage using SQLite.
- Session detection and analysis.
- Application usage and switching analysis.
- Behavioral pattern detection.
- Event relationship exploration.
- Backward tracing of recorded activity.
- Natural-language-style activity queries.

All activity records are stored locally in an SQLite database.

## Features

### 1. Activity Collection
- Monitors foreground application activity on Windows.
- Records application activity events.
- Stores activity history locally.

### 2. Activity Timeline
- Displays recorded desktop activity chronologically.
- Allows users to explore their application history.
- Supports filtering activity by application.

### 3. Session Detection
- Groups activity events into sessions.
- Provides session-level information.
- Allows investigation of events belonging to individual sessions.

### 4. Application Usage Analytics
- Analyzes application usage and recorded activity duration.
- Summarizes time spent across applications.
- Helps identify application usage patterns.

### 5. Application Switching Analysis
- Examines transitions between applications.
- Identifies repeated application-switching sequences.
- Analyzes recurring switching patterns.

### 6. Behavioral Signals
- Detects recurring patterns in application activity.
- Highlights repeated application transitions.
- Provides behavioral insights based on recorded events.

*Behavioral signals indicate observable patterns; they do not establish a user's intentions, attention or productivity.*

### 7. Event Relationships
- Explores relationships between recorded activity events.
- Provides a graph-based view of activity connections.
- Helps investigate how events relate to one another.

### 8. Backward Tracing
- Investigates activity surrounding a selected event.
- Helps reconstruct the sequence of recorded application activity.
- Provides additional context for understanding past activity.

### 9. Ask Retrace
- Provides a natural-language-style interface for querying activity history.
- Allows users to investigate questions about previously recorded activity.
- Connects queries with recorded application activity.

### 10. Interactive Dashboard
- Provides a browser-based interface.
- Organizes activity information into different dashboard views.
- Includes collector status and tracking controls.
- Combines activity history, analytics and investigation tools.

---

## Architecture

Retrace follows a modular processing architecture.

```text
┌──────────────────────────────┐
│     Windows Activity         │
│         Collector            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Event Storage          │
│          SQLite              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Activity Analysis       │
│                              │
│  • Timeline                  │
│  • Session Detection         │
│  • Usage Analysis            │
│  • Switch Detection          │
│  • Behavioral Signals        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Investigation Engine      │
│                              │
│  • Event Relationships       │
│  • Backward Tracing          │
│  • Activity Queries          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Flask Dashboard        │
│                              │
│     HTML / CSS / JavaScript  │
└──────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Database | SQLite |
| Windows Integration | pywin32 |
| Process Information | psutil |
| Frontend | HTML, CSS, JavaScript |
| Version Control | Git |

---

## Project Structure

```text
retrace/
│
├── analysis/
│   ├── assign_sessions.py
│   ├── backward_trace.py
│   ├── behavior_signals.py
│   ├── durations.py
│   ├── history.py
│   ├── patterns.py
│   ├── query_engine.py
│   ├── query_parser.py
│   ├── query_runner.py
│   ├── relationships.py
│   ├── repeated_switches.py
│   ├── repeated_switch_counts.py
│   ├── session_analysis.py
│   ├── session_detection.py
│   ├── switch_analysis.py
│   ├── switch_detection.py
│   ├── timeline.py
│   └── ...
│
├── api/
│   └── dashboard.py
│
├── collector/
│   ├── activity_collector.py
│   └── controller.py
│
├── database/
│   └── database.py
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
│
├── models/
│   ├── application.py
│   └── event.py
│
├── tests/
│   ├── test_collector_controller.py
│   ├── test_specific_date.py
│   └── test_yesterday.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation and Setup

### Prerequisites

- Windows operating system.
- Python 3.13 or a compatible Python version.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/Suryansh-og/retrace.git
cd retrace
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running Retrace

From the project root directory, execute:

```bash
python -m api.dashboard
```

Once the Flask server starts, open your browser and navigate to:

**http://127.0.0.1:5000/dashboard**

The dashboard initializes the SQLite database and creates the required tables automatically if they do not already exist.

The activity collector can be managed through the dashboard.

> **Important:** Retrace is designed for Windows desktop activity collection. The collector requires an appropriate Windows environment and permissions.

---

## Database and Data Storage

Retrace uses SQLite for local activity storage.

The database module manages two primary tables:

| Table | Purpose |
|---|---|
| `events` | Stores recorded application activity events. |
| `sessions` | Stores detected activity sessions. |

The database is initialized automatically when the dashboard starts.

Activity information is stored locally rather than requiring an external database server.

---

## Running Tests

Retrace includes automated tests for collector lifecycle management and activity queries.

Run the test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

### Python Syntax Validation

```bash
python -m compileall -q .
```

---

## Privacy and Responsible Use

Privacy is an important consideration for desktop activity monitoring.

- Activity records are stored locally in SQLite.
- Application names and window titles may reveal sensitive information.
- Users should understand what information is being collected.
- Obtain appropriate consent before monitoring another person's activity.
- Do not publicly share personal activity databases.

Behavioral analysis should be interpreted carefully. Repeated application switching does not necessarily indicate distraction or reduced productivity.

---

## Future Development

Potential areas for further development include:

- More advanced activity relationship analysis.
- Improved behavioral pattern explanations.
- Expanded reporting and visualization.
- Additional privacy and data-management controls.
- More comprehensive automated testing.
- Improved activity investigation capabilities.

---

## Author

**Suryansh Yadav**

B.Tech — Information Technology

GitHub: [@Suryansh-og](https://github.com/Suryansh-og)

---

## Project Status

Retrace is developed as a Software Engineering Mini Project.

The current implementation includes activity collection, local storage, session analysis, behavioral analysis, event investigation and an interactive Flask dashboard.

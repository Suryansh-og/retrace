\# Retrace



Retrace is an AI-powered digital behavior intelligence system that analyzes digital activity history and behavioral patterns to understand how digital events relate to task interruption, distraction, and task abandonment.



\## Current Mini Project



The current version implements the Level-1 Retrace pipeline:



Activity Collection → History Storage → Timeline → Event Relationships → Backward Tracing → Basic Pattern Analysis → Dashboard



\## Features



\- Windows foreground application activity collection

\- SQLite event history

\- Session detection

\- Session-based event analysis

\- Application usage analysis

\- Application switching analysis

\- Repeated-switch behavior signals

\- Backward event tracing

\- Flask web dashboard



\## Tech Stack



\- Python

\- Flask

\- SQLite

\- pywin32

\- psutil

\- HTML

\- CSS

\- JavaScript



\## Project Structure



```text

retrace/

├── collector/

├── database/

├── models/

├── analysis/

├── api/

├── frontend/

├── .gitignore

└── README.md


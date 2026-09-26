import sqlite3
from collections import Counter

DATABASE_NAME = "retrace.db"


def get_applications():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT application
        FROM events
        WHERE application != ''
    """)

    applications = cursor.fetchall()

    connection.close()

    return [application[0] for application in applications]


applications = get_applications()

counts = Counter(applications)

print("\n===== APPLICATION PATTERNS =====\n")

for application, count in counts.most_common():

    print(f"{application}  ->  {count} times")
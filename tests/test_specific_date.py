
import unittest
from unittest.mock import patch

from analysis import query_engine


class TestSpecificDateQueries(unittest.TestCase):

    def setUp(self):
        self.target_date = "2026-10-30"

        # Event structure:
        # id, timestamp, application, activity_type,
        # context, task_id, session_id

        self.sample_events = [
            (
                1,
                "2026-10-30T10:00:00",
                "Brave",
                "application_switch",
                "Google Search",
                None,
                1
            ),
            (
                2,
                "2026-10-30T10:05:00",
                "Visual Studio Code",
                "application_switch",
                "main.py",
                None,
                1
            ),
            (
                3,
                "2026-10-29T15:00:00",
                "Brave",
                "application_switch",
                "YouTube",
                None,
                1
            ),
            (
                4,
                "2026-10-30T11:00:00",
                "Brave",
                "application_switch",
                "GitHub",
                None,
                1
            )
        ]

    @patch("analysis.query_engine.get_events")
    def test_find_by_date(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_date(self.target_date)

        self.assertEqual(len(results), 3)

        for event in results:
            self.assertEqual(event[1][:10], self.target_date)

    @patch("analysis.query_engine.get_events")
    def test_find_by_application_date(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_application_date(
            "Brave",
            self.target_date
        )

        self.assertEqual(len(results), 2)

        for event in results:
            self.assertEqual(event[2].lower(), "brave")
            self.assertEqual(event[1][:10], self.target_date)

    @patch("analysis.query_engine.get_events")
    def test_application_search_is_case_insensitive(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_application_date(
            "BRAVE",
            self.target_date
        )

        self.assertEqual(len(results), 2)

    @patch("analysis.query_engine.get_events")
    def test_no_events_for_unmatched_date(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_date("2026-11-01")

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

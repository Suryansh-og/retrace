
import unittest
from datetime import datetime as RealDateTime
from unittest.mock import patch

from analysis import query_engine


class FixedDateTime:

    @staticmethod
    def now():
        return RealDateTime(2026, 10, 31)

    @staticmethod
    def fromisoformat(value):
        return RealDateTime.fromisoformat(value)


class TestYesterdayQueries(unittest.TestCase):

    def setUp(self):

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
                "2026-10-30T11:00:00",
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
                "2026-10-30T12:00:00",
                "Brave",
                "application_switch",
                "GitHub",
                None,
                1
            ),
            (
                5,
                "2026-10-31T09:00:00",
                "Brave",
                "application_switch",
                "Today",
                None,
                1
            )
        ]

    @patch("analysis.query_engine.datetime", FixedDateTime)
    @patch("analysis.query_engine.get_events")
    def test_find_yesterday(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_yesterday()

        self.assertEqual(len(results), 3)

        for event in results:
            self.assertEqual(event[1][:10], "2026-10-30")

    @patch("analysis.query_engine.datetime", FixedDateTime)
    @patch("analysis.query_engine.get_events")
    def test_find_by_application_yesterday(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_application_yesterday(
            "Brave"
        )

        self.assertEqual(len(results), 2)

        for event in results:
            self.assertEqual(event[2], "Brave")
            self.assertEqual(event[1][:10], "2026-10-30")

    @patch("analysis.query_engine.datetime", FixedDateTime)
    @patch("analysis.query_engine.get_events")
    def test_application_search_is_case_insensitive(self, mock_get_events):

        mock_get_events.return_value = self.sample_events

        results = query_engine.find_by_application_yesterday(
            "BRAVE"
        )

        self.assertEqual(len(results), 2)

    @patch("analysis.query_engine.datetime", FixedDateTime)
    @patch("analysis.query_engine.get_events")
    def test_no_events_for_yesterday(self, mock_get_events):

        mock_get_events.return_value = [
            self.sample_events[-1]
        ]

        results = query_engine.find_yesterday()

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

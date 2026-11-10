
import threading
import unittest
from unittest.mock import patch

from collector import controller


class TestCollectorController(unittest.TestCase):

    def setUp(self):
        controller.stop_event.clear()
        controller._collector_thread = None

    def tearDown(self):
        controller.stop_event.set()

        thread = controller._collector_thread

        if thread is not None and thread.is_alive():
            thread.join(timeout=5)

        controller._collector_thread = None
        controller.stop_event.clear()

    def test_initial_status_is_stopped(self):
        self.assertEqual(
            controller.get_collector_status(),
            "stopped"
        )

    def test_start_collector(self):
        finished = threading.Event()

        def mock_collector():
            finished.wait(timeout=5)

        with patch.object(
            controller,
            "collect_activity",
            side_effect=mock_collector
        ):
            result = controller.start_collector()

            self.assertEqual(result["status"], "running")
            self.assertEqual(
                controller.get_collector_status(),
                "running"
            )

            controller.stop_event.set()
            finished.set()

            thread = controller._collector_thread
            thread.join(timeout=5)

            self.assertFalse(thread.is_alive())

    def test_start_already_running_collector(self):
        finished = threading.Event()

        def mock_collector():
            finished.wait(timeout=5)

        with patch.object(
            controller,
            "collect_activity",
            side_effect=mock_collector
        ):
            first_result = controller.start_collector()
            first_thread = controller._collector_thread

            second_result = controller.start_collector()

            self.assertEqual(first_result["status"], "running")
            self.assertEqual(second_result["status"], "running")
            self.assertIs(
                controller._collector_thread,
                first_thread
            )

            controller.stop_event.set()
            finished.set()
            first_thread.join(timeout=5)

            self.assertFalse(first_thread.is_alive())

    def test_stop_inactive_collector(self):
        result = controller.stop_collector()

        self.assertEqual(result["status"], "stopped")
        self.assertEqual(
            controller.get_collector_status(),
            "stopped"
        )

    def test_stop_running_collector(self):
        finished = threading.Event()

        def mock_collector():
            finished.wait(timeout=5)

        with patch.object(
            controller,
            "collect_activity",
            side_effect=mock_collector
        ):
            controller.start_collector()

            self.assertEqual(
                controller.get_collector_status(),
                "running"
            )

            finished.set()
            result = controller.stop_collector()

            self.assertEqual(result["status"], "stopped")
            self.assertEqual(
                controller.get_collector_status(),
                "stopped"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

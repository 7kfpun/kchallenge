import unittest
from unittest.mock import MagicMock, patch
from utils.worker import Worker


class TestWorker(unittest.TestCase):
    def setUp(self):
        self.mock_task_class = MagicMock()
        self.mock_task_class.__name__ = "MockTask"
        self.worker = Worker(task_class=self.mock_task_class, retry_limit=3, interval=1)

    @patch("time.sleep", return_value=None)  # Prevent actual sleep during tests
    def test_worker_stops_gracefully(self, _):
        # Mock task execution
        self.mock_task_class.get_tasks = MagicMock(return_value=["task1"])
        self.mock_task_class.execute_task = MagicMock(
            side_effect=Exception("Test Error")
        )

        # Patch `running` to stop after one iteration
        with patch.object(
            self.worker, "running", new_callable=lambda: iter([True, False])
        ):
            self.worker.run()

        self.mock_task_class.get_tasks.assert_called_once()
        self.mock_task_class.execute_task.assert_called_with("task1")


if __name__ == "__main__":
    unittest.main()

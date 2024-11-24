import unittest
from unittest.mock import MagicMock, patch
from tasks.cache_stats_task import CacheStatsTask


class TestCacheStatsTask(unittest.TestCase):
    @patch("tasks.cache_stats_task.cache")
    @patch("tasks.cache_stats_task.logger")
    def test_execute_task_logs_stats(self, mock_logger, mock_cache):
        # Mock cache stats
        mock_cache.stats.return_value = {"hits": 10, "misses": 5}

        # Call the method
        CacheStatsTask.execute_task(None)

        # Assert the log was called with the expected stats
        mock_logger.info.assert_called_with(
            "[CacheStatsTask] Cache Stats: %s", {"hits": 10, "misses": 5}
        )


if __name__ == "__main__":
    unittest.main()

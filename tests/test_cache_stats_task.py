"""
Tests for the cache stats task.
"""

import asyncio
import unittest
from unittest.mock import patch

from app.api.cache import cache
from app.tasks.cache_stats_task import log_cache_stats


class TestCacheStatsTask(unittest.TestCase):
    """
    Tests for the cache stats task.
    """

    @patch("app.tasks.cache_stats_task.logger")
    def test_log_cache_stats(self, mock_logger):
        """
        Test logging cache statistics.
        """
        mock_cache_stats = {
            "hits": 10,
            "misses": 5,
            "total_requests": 15,
            "hit_ratio": 0.6667,
        }
        with patch.object(cache, "stats", return_value=mock_cache_stats):
            asyncio.run(log_cache_stats())
            mock_logger.info.assert_called_with(
                "[CacheStatsTask] Cache Stats: %s", mock_cache_stats
            )

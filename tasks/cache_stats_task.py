"""
Task for logging cache statistics periodically.
"""

# pylint: disable=too-few-public-methods
import logging
from services.marvel_service import cache

logger = logging.getLogger(__name__)


class CacheStatsTask:
    """
    Task for logging cache statistics periodically.
    """

    @staticmethod
    def execute_task(_):
        """
        Log cache statistics. No task-specific key needed.
        """
        stats = cache.stats()
        logger.info("[CacheStatsTask] Cache Stats: %s", stats)

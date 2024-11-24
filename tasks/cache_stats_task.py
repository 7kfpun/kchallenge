"""
CacheStatsTask: Logs cache statistics at regular intervals.
"""

import logging
from marvel.cache import cache

logger = logging.getLogger(__name__)


class CacheStatsTask:
    """
    Task to log cache statistics.
    """

    @staticmethod
    def enqueue_tasks(task_queue):
        """
        Enqueue the cache stats task into the shared task queue.
        :param task_queue: The shared task queue managed by WorkerManager.
        """
        task = {"task_name": "cache_stats", "params": {}}
        if not task_queue.full():
            task_queue.put(task)
            logger.info("[CacheStatsTask] Cache stats task enqueued.")

    @staticmethod
    def execute_task(task):
        """
        Log cache statistics.
        :param task: A dictionary containing the task name and parameters.
        """
        task_name = task.get("task_name")
        if task_name != "cache_stats":
            logger.warning("[CacheStatsTask] Invalid task name: %s", task_name)
            return

        # Log cache stats
        stats = cache.stats()
        logger.info("[CacheStatsTask] Cache Stats: %s", stats)

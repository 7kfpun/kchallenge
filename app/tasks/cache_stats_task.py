"""
Logs cache statistics at regular intervals.
"""

import logging

from app.cache import cache
from app.workers.broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def log_cache_stats():
    """
    Log cache statistics.
    """
    stats = cache.stats()
    logger.info("[CacheStatsTask] Cache Stats: %s", stats)

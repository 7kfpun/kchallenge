"""
Cache module for Marvel API.
"""

import logging
import time

logger = logging.getLogger(__name__)


class Cache:
    """
    Cache implementation.
    """

    def __init__(self, maxsize=1000, ttl=300):
        """
        Custom Cache implementation.
        :param maxsize: Maximum number of items in the cache.
        :param ttl: Time-to-live for cache entries in seconds.
        """
        self.cache = {}
        self.ttl = ttl
        self.maxsize = maxsize
        self.hit_count = 0
        self.miss_count = 0

    def _evict_if_needed(self):
        """
        Evict the oldest items if the cache exceeds maxsize.
        """
        while len(self.cache) > self.maxsize:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]["timestamp"])
            logger.info("Evicting key: %s", oldest_key)
            del self.cache[oldest_key]

    def get(self, key):
        """
        Retrieve an item from the cache.
        :param key: Cache key.
        :return: Cached value or None if not found or expired.
        """
        entry = self.cache.get(key)
        if entry:
            if time.time() - entry["timestamp"] < self.ttl:
                self.hit_count += 1
                logger.info("Cache hit for key: %s", key)
                return entry["value"]

            logger.info("Cache expired for key: %s", key)
            del self.cache[key]

        self.miss_count += 1
        logger.info("Cache miss for key: %s", key)
        return None

    def set(self, key, value):
        """
        Add an item to the cache.
        :param key: Cache key.
        :param value: Cache value.
        """
        self.cache[key] = {"value": value, "timestamp": time.time()}
        self._evict_if_needed()

    def stats(self):
        """
        Get cache statistics.
        :return: Dictionary containing hit, miss, and hit ratio stats.
        """
        total_requests = self.hit_count + self.miss_count
        hit_ratio = self.hit_count / max(1, total_requests)
        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "total_requests": total_requests,
            "hit_ratio": hit_ratio,
        }

    def clear(self):
        """
        Clear the cache and reset stats.
        """
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Cache cleared.")

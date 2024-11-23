"""
Cache module for Marvel API.
"""

from collections import OrderedDict
from urllib.parse import urlencode
import time
import logging

logger = logging.getLogger(__name__)


class Cache:
    """
    Cache.
    """

    def __init__(self, maxsize=1000, ttl=300):
        """
        Initialize the cache with hit and miss counters.
        :param maxsize: Maximum number of items in the cache.
        :param ttl: Time-to-live for cache entries in seconds.
        """
        self.store = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str):
        """
        Retrieve a value from the cache if it exists and is not expired.
        Increments hit or miss counters.
        """
        if key in self.store:
            value, timestamp = self.store[key]
            if time.time() - timestamp < self.ttl:
                self.hit_count += 1
                self.store.move_to_end(key)
                logger.info("Cache hit for key: %s", key)
                return value

            # Remove expired entry
            del self.store[key]
            self.miss_count += 1
            logger.info("Cache miss (expired) for key: %s", key)
            return None

        self.miss_count += 1
        logger.info("Cache miss for key: %s", key)
        return None

    def set(self, key, value):
        """
        Add or update a value in the cache with the current timestamp.
        Evicts the oldest item if the cache exceeds maxsize.
        """
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = (value, time.time())

        if len(self.store) > self.maxsize:
            # Evict the oldest entry
            evicted_key, _ = self.store.popitem(last=False)
            logger.info("Evicted key: %s", evicted_key)

    def keys(self):
        """
        Return all keys in the cache.
        """
        return list(self.store.keys())

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
        Clear the cache and reset counters.
        """
        self.store.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Cache cleared.")


def generate_cache_key(params: dict) -> str:
    """
    Generate a unique cache key for API caching based on query parameters.

    :param params: Dictionary of query parameters.
    :return: A unique string representing the cache key.
    """
    # Sort parameters to ensure consistent ordering
    sorted_params = {k: v for k, v in sorted(params.items()) if v is not None}
    return urlencode(sorted_params, doseq=True)

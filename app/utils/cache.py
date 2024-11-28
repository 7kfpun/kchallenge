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
        self.etags = {}
        self.maxsize = maxsize
        self.ttl = ttl
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str):
        """
        Get a value from the cache, including its Etag.
        """
        if key in self.store:
            value, timestamp = self.store[key]
            if time.time() - timestamp < self.ttl:
                self.hit_count += 1
                return value

            self.store.pop(key)
            self.etags.pop(key, None)
            self.miss_count += 1
            return None

        self.miss_count += 1
        return None

    def set(self, key: str, value: dict, etag: str = ""):
        """
        Add or update a value in the cache with the current timestamp.
        Evicts the oldest item if the cache exceeds maxsize.
        """
        if key in self.store:
            self.store.move_to_end(key)  # Mark as recently accessed
        self.store[key] = (value, time.time())
        if etag:
            self.etags[key] = etag

        if len(self.store) > self.maxsize:
            # Evict the oldest entry
            evicted_key, _ = self.store.popitem(last=False)
            self.etags.pop(evicted_key, None)  # Remove the associated Etag
            logger.info("Evicted key: %s", evicted_key)

    def keys(self):
        """
        Return all keys in the cache.
        """
        return list(self.store.keys())

    def get_etag(self, key):
        """
        Get the Etag for a cached item.
        """
        return self.etags.get(key)

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
        self.etags.clear()
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

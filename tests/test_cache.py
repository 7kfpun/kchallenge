"""
Test the Cache class.
"""

import unittest
from unittest.mock import patch
from app.utils.cache import Cache, generate_cache_key
from app.grpc_services.marvel_service import MarvelService


class TestCache(unittest.TestCase):
    def setUp(self):
        """
        Set up a Cache instance before each test.
        """
        self.cache = Cache(maxsize=3, ttl=300)
        self.service = MarvelService()

    def test_set_and_get(self):
        """
        Test adding and retrieving items from the cache.
        """
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        # Test getting existing keys
        self.assertEqual(
            self.cache.get("key1"), "value1", "Failed to retrieve cached value."
        )
        self.assertEqual(
            self.cache.get("key2"), "value2", "Failed to retrieve cached value."
        )

        # Test hit and miss counts
        self.assertEqual(self.cache.hit_count, 2, "Hit count incorrect.")
        self.assertEqual(self.cache.miss_count, 0, "Miss count incorrect.")

    def test_eviction_policy(self):
        """
        Test that the cache evicts the least recently used item when maxsize is exceeded.
        """
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        self.cache.set("key4", "value4")  # Should evict "key1"

        self.assertIsNone(self.cache.get("key1"), "Eviction policy failed.")
        self.assertEqual(self.cache.get("key2"), "value2", "Unexpected eviction.")
        self.assertEqual(self.cache.get("key3"), "value3", "Unexpected eviction.")
        self.assertEqual(self.cache.get("key4"), "value4", "Unexpected eviction.")

    @patch("time.time", return_value=1000)
    def test_ttl_expiry(self, mock_time):
        """
        Test that items expire after the TTL is exceeded.
        """
        self.cache.set("key1", "value1")

        # Mock time to simulate an expired cache entry
        mock_time.return_value = 1301  # TTL is 300, so this is expired
        self.assertIsNone(
            self.cache.get("key1"), "Expired cache entry should return None."
        )
        self.assertEqual(
            self.cache.miss_count, 1, "Miss count not incremented for expired entry."
        )

    def test_etag_eviction(self):
        """
        Test that Etags are evicted along with their cache entries.
        """
        self.cache.set("key1", "value1", etag="etag1")
        self.cache.set("key2", "value2", etag="etag2")
        self.cache.set("key3", "value3", etag="etag3")
        self.cache.set("key4", "value4", etag="etag4")  # Exceeds maxsize

        # Ensure "key1" is evicted
        self.assertIsNone(
            self.cache.get("key1"), "Eviction policy failed for cache entry."
        )
        self.assertIsNone(
            self.cache.get_etag("key1"), "Eviction policy failed for Etag."
        )

    def test_ttl_expiry_for_etag(self):
        """
        Test that expired cache entries also remove their Etags.
        """
        with unittest.mock.patch("time.time", return_value=1000):
            self.cache.set("key1", "value1", etag="etag1")

        with unittest.mock.patch("time.time", return_value=1301):  # TTL is 300
            self.assertIsNone(
                self.cache.get("key1"), "Expired cache entry should be removed."
            )
            self.assertIsNone(
                self.cache.get_etag("key1"), "Expired Etag should be removed."
            )

    def test_set_and_get_etag(self):
        """
        Test storing and retrieving Etags.
        """
        key = "test_key"
        etag = "etag123"
        self.cache.set(key, {"data": "test_data"}, etag=etag)

        # Check Etag retrieval
        self.assertEqual(
            self.cache.get_etag(key), etag, "Failed to retrieve correct Etag."
        )

    def test_clear(self):
        """
        Test clearing all cache entries.
        """
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()

        self.assertEqual(self.cache.hit_count, 0, "Hit count should reset after clear.")
        self.assertEqual(
            self.cache.miss_count, 0, "Miss count should reset after clear."
        )

    def test_stats(self):
        """
        Test that cache statistics are accurate.
        """
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss

        stats = self.cache.stats()
        self.assertEqual(stats["hits"], 1, "Stats - Hit count incorrect.")
        self.assertEqual(stats["misses"], 1, "Stats - Miss count incorrect.")
        self.assertEqual(
            stats["total_requests"], 2, "Stats - Total requests count incorrect."
        )
        self.assertAlmostEqual(
            stats["hit_ratio"], 0.5, msg="Stats - Hit ratio incorrect."
        )

    def test_generate_cache_key(self):
        """
        Test that the cache key is generated correctly.
        """
        self.assertEqual(generate_cache_key({"a": 1, "b": 2}), "a=1&b=2")
        self.assertEqual(generate_cache_key({"b": 1, "a": 2}), "a=2&b=1")


if __name__ == "__main__":
    unittest.main()

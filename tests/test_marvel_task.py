"""
Tests for the Marvel task.
"""

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from app.cache import cache
from app.tasks.marvel_task import update_marvel_cache, enqueue_marvel_tasks


class TestMarvelTask(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the Marvel task.
    """

    def setUp(self):
        cache.clear()

    @patch("app.tasks.marvel_task.get_marvel_characters", new_callable=AsyncMock)
    async def test_update_marvel_cache_success(self, mock_get_marvel_characters):
        """
        Test the update_marvel_cache function.
        """
        mock_get_marvel_characters.return_value = MagicMock(
            status_code=200,
            json=MagicMock(
                return_value={
                    "data": {
                        "results": [{"id": 1, "name": "Spider-Man"}],
                    }
                }
            ),
            headers={"Etag": "etag-value"},
        )

        cache_key = "name=Spider-Man&limit=10"
        cache.set(cache_key, None)  # Simulate no cache entry
        await update_marvel_cache(cache_key)

        self.assertIsNotNone(cache.get(cache_key))
        self.assertEqual(cache.get_etag(cache_key), "etag-value")
        mock_get_marvel_characters.assert_awaited_once()

    @patch("app.tasks.marvel_task.get_marvel_characters", new_callable=AsyncMock)
    async def test_update_marvel_cache_not_modified(self, mock_get_marvel_characters):
        """
        Test the update_marvel_cache function when the response is not modified.
        """
        mock_get_marvel_characters.return_value = MagicMock(status_code=304)

        cache_key = "name=Spider-Man&limit=10"
        cache.set(cache_key, {"cached": "data"}, etag="etag-value")  # Simulate cache
        await update_marvel_cache(cache_key)

        self.assertEqual(cache.get(cache_key), {"cached": "data"})
        mock_get_marvel_characters.assert_awaited_once()

    @patch("app.tasks.marvel_task.get_marvel_characters", new_callable=AsyncMock)
    async def test_update_marvel_cache_invalid_response(
        self, mock_get_marvel_characters
    ):
        """
        Test the update_marvel_cache function when the response is invalid.
        """
        mock_get_marvel_characters.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={}),
        )

        cache_key = "name=Spider-Man&limit=10"
        cache.set(cache_key, None)  # Simulate no cache entry
        await update_marvel_cache(cache_key)

        self.assertIsNone(cache.get(cache_key))
        mock_get_marvel_characters.assert_awaited_once()

    @patch("app.tasks.marvel_task.update_marvel_cache.kiq", new_callable=AsyncMock)
    async def test_enqueue_marvel_tasks(self, mock_update_marvel_cache_kiq):
        """
        Test the enqueue_marvel_tasks function.
        """
        cache.set("key1", {"some": "data"})
        cache.set("key2", {"other": "data"})

        await enqueue_marvel_tasks()

        self.assertEqual(mock_update_marvel_cache_kiq.await_count, 2)
        mock_update_marvel_cache_kiq.assert_any_await("key1")
        mock_update_marvel_cache_kiq.assert_any_await("key2")


if __name__ == "__main__":
    unittest.main()

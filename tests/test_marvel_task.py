import unittest
from unittest.mock import MagicMock, patch
from tasks.marvel_task import MarvelTask


class TestMarvelTask(unittest.TestCase):
    @patch("tasks.marvel_task.cache")
    @patch("tasks.marvel_task.get_marvel_characters")
    def test_execute_task_cache_update(self, mock_get_marvel_characters, mock_cache):
        # Mock cache and API response
        mock_cache.get_etag.return_value = "etag123"
        mock_get_marvel_characters.return_value = MagicMock(
            status_code=200,
            headers={"Etag": "new-etag"},
            json=MagicMock(
                return_value={"data": {"results": [{"id": 1, "name": "Spider-Man"}]}}
            ),
        )

        MarvelTask.execute_task("worker:{'name': 'Spider-Man'}")

        mock_cache.set.assert_called_with(
            "worker:{'name': 'Spider-Man'}",
            [{"id": 1, "name": "Spider-Man"}],
            etag="new-etag",
        )

    @patch("tasks.marvel_task.cache")
    @patch("tasks.marvel_task.get_marvel_characters")
    def test_execute_task_no_update_needed(
        self, mock_get_marvel_characters, mock_cache
    ):
        # Mock 304 Not Modified response
        mock_cache.get_etag.return_value = "etag123"
        mock_get_marvel_characters.return_value = MagicMock(status_code=304)

        MarvelTask.execute_task("worker:{'name': 'Spider-Man'}")

        mock_cache.set.assert_not_called()


if __name__ == "__main__":
    unittest.main()

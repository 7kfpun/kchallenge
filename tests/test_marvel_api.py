"""
Tests for the Marvel API.
"""

import unittest
from unittest.mock import AsyncMock, patch
from app.api.marvel_api import get_marvel_characters


class TestMarvelAPI(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the Marvel API.
    """

    @patch("app.api.marvel_api.httpx.AsyncClient.get")
    async def test_get_marvel_characters_success(self, mock_httpx_get):
        """
        Test successful response from Marvel API.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"results": [{"name": "Spider-Man"}]}
        }
        mock_response.raise_for_status = AsyncMock()  # Ensure this is awaitable
        mock_httpx_get.return_value = mock_response

        response = await get_marvel_characters(name="Spider-Man", limit=1)
        self.assertEqual(
            (await response.json())["data"]["results"][0]["name"], "Spider-Man"
        )
        mock_httpx_get.assert_called_once()

    @patch("app.api.marvel_api.httpx.AsyncClient.get")
    async def test_get_marvel_characters_not_modified(self, mock_httpx_get):
        """
        Test not-modified (304) response from Marvel API.
        """
        mock_response = AsyncMock()
        mock_response.status_code = 304
        mock_response.raise_for_status = AsyncMock()  # Ensure this is awaitable
        mock_httpx_get.return_value = mock_response

        response = await get_marvel_characters(name="Spider-Man", limit=1)
        self.assertEqual(response.status_code, 304)
        mock_httpx_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()

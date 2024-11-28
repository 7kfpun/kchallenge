"""
Tests for the Marvel service.
"""

# pylint: disable=no-member
import unittest
import asyncio
from unittest.mock import patch, MagicMock

from app.grpc_services.marvel_service import MarvelService
from app.grpc_services.proto import marvel_pb2


class TestMarvelService(unittest.TestCase):
    """
    Tests for the Marvel service.
    """

    def setUp(self):
        self.marvel_service = MarvelService()
        self.mock_request = marvel_pb2.CharacterRequest(
            name="Spider-Man", limit=10, offset=0
        )
        self.mock_context = MagicMock()

    def test_get_characters_successful_api_call(self):
        """
        Test the GetCharacters method when the API call is successful.
        """

        # Async test requires a slightly different approach with asyncio
        async def run_test():
            # Mock the get_marvel_characters to return a successful response
            with patch(
                "app.grpc_services.marvel_service.get_marvel_characters"
            ) as mock_get_characters:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": {
                        "results": [
                            {
                                "id": 1009610,
                                "name": "Spider-Man",
                                "description": "Bitten by a radioactive spider",
                                "thumbnail": {
                                    "path": "http://example.com/spider-man",
                                    "extension": "jpg",
                                },
                            }
                        ]
                    }
                }
                mock_response.headers = {"Etag": "test-etag"}
                mock_get_characters.return_value = mock_response

                # Mock cache
                with patch("app.grpc_services.marvel_service.cache") as mock_cache:
                    mock_cache.get.return_value = None
                    mock_cache.get_etag.return_value = None

                    # Call the method
                    response = await self.marvel_service.GetCharacters(
                        self.mock_request, self.mock_context
                    )

                    # Assertions
                    self.assertEqual(len(response.characters), 1)
                    self.assertEqual(response.characters[0].name, "Spider-Man")
                    self.assertEqual(response.characters[0].id, 1009610)

        # Run the async test
        asyncio.run(run_test())

    def test_get_characters_cached_response(self):
        """
        Test the GetCharacters method when the response is cached.
        """

        async def run_test():
            # Mock cache with existing response
            cached_data = {
                "data": {
                    "results": [
                        {
                            "id": 1009610,
                            "name": "Spider-Man",
                            "description": "Bitten by a radioactive spider",
                            "thumbnail": {
                                "path": "http://example.com/spider-man",
                                "extension": "jpg",
                            },
                        }
                    ]
                }
            }

            with patch("app.grpc_services.marvel_service.cache") as mock_cache:
                mock_cache.get.return_value = cached_data
                mock_cache.get_etag.return_value = "cached-etag"

                # Call the method
                response = await self.marvel_service.GetCharacters(
                    self.mock_request, self.mock_context
                )

                # Assertions
                self.assertEqual(len(response.characters), 1)
                self.assertEqual(response.characters[0].name, "Spider-Man")

        asyncio.run(run_test())

    def test_get_characters_error_handling(self):
        """
        Test the GetCharacters method when the API call fails.
        """

        async def run_test():
            # Mock get_marvel_characters to raise an exception
            with patch(
                "app.grpc_services.marvel_service.get_marvel_characters",
                side_effect=Exception("API Error"),
            ):
                # Call the method
                response = await self.marvel_service.GetCharacters(
                    self.mock_request, self.mock_context
                )

                # Assertions
                self.assertEqual(len(response.characters), 0)
                self.mock_context.set_code.assert_called_with(
                    self.mock_context.Code.INTERNAL
                )
                self.mock_context.set_details.assert_called_with(
                    "Failed to fetch characters."
                )

        asyncio.run(run_test())

    def test_get_characters_not_modified_response(self):
        """
        Test the GetCharacters method when the response is not modified.
        """

        async def run_test():
            # Mock the get_marvel_characters to return a 304 Not Modified response
            with patch(
                "app.grpc_services.marvel_service.get_marvel_characters"
            ) as mock_get_characters:
                mock_response = MagicMock()
                mock_response.status_code = 304

                # Mock cached data
                cached_data = {
                    "data": {
                        "results": [
                            {
                                "id": 1009610,
                                "name": "Spider-Man",
                                "description": "Bitten by a radioactive spider",
                                "thumbnail": {
                                    "path": "http://example.com/spider-man",
                                    "extension": "jpg",
                                },
                            }
                        ]
                    }
                }

                with patch("app.grpc_services.marvel_service.cache") as mock_cache:
                    mock_cache.get.return_value = cached_data
                    mock_get_characters.return_value = mock_response

                    # Call the method
                    response = await self.marvel_service.GetCharacters(
                        self.mock_request, self.mock_context
                    )

                    # Assertions
                    self.assertEqual(len(response.characters), 1)
                    self.assertEqual(response.characters[0].name, "Spider-Man")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

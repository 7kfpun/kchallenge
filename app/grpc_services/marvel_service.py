"""
Marvel service for fetching Marvel characters.
"""

# pylint: disable=no-member,broad-exception-caught
import logging

from app.api.marvel_api import get_marvel_characters
from app.grpc_services.proto import marvel_pb2
from app.grpc_services.proto import marvel_pb2_grpc
from app.api.cache import cache
from app.utils.cache import generate_cache_key

logger = logging.getLogger(__name__)


class MarvelService(marvel_pb2_grpc.MarvelServiceServicer):
    """
    Marvel service for fetching Marvel characters.
    """

    async def GetCharacters(self, request, context):
        """
        Fetch Marvel characters based on the gRPC request parameters.
        Uses caching to avoid redundant API calls.
        """
        query_params = {
            "name": request.name,
            "name_starts_with": request.name_starts_with,
            "modified_since": request.modified_since,
            "comics": list(request.comics),
            "series": list(request.series),
            "events": list(request.events),
            "stories": list(request.stories),
            "order_by": request.order_by,
            "limit": request.limit,
            "offset": request.offset,
        }

        cache_key = generate_cache_key(query_params)
        cached_etag = cache.get_etag(cache_key)
        headers = {"If-None-Match": cached_etag} if cached_etag else {}

        cached_response = cache.get(cache_key)
        if cached_response:
            return self._build_response_from_cache(cached_response)

        try:
            response = await get_marvel_characters(headers=headers, **query_params)

            if response.status_code == 304:  # Not Modified
                cached_data = cache.get(cache_key)
                return self._build_response_from_cache(cached_data)

            response_data = response.json()

            new_etag = response.headers.get("Etag")
            cache.set(cache_key, response_data, etag=new_etag)

            return self._build_response_from_api(response_data)

        except Exception as e:
            logger.error("[MarvelService] Error fetching characters: %s", e)
            context.set_code(context.Code.INTERNAL)
            context.set_details("Failed to fetch characters.")
            return marvel_pb2.CharacterResponse()

    def _build_response_from_api(self, api_response):
        """
        Convert the Marvel API response into a gRPC response format.
        """
        characters = [
            marvel_pb2.Character(
                id=result.get("id", 0),
                name=result.get("name", ""),
                description=result.get("description", ""),
                thumbnail=(
                    marvel_pb2.Image(
                        path=result["thumbnail"]["path"],
                        extension=result["thumbnail"]["extension"],
                    )
                    if result.get("thumbnail")
                    else None
                ),
            )
            for result in api_response.get("data", {}).get("results", [])
        ]

        return marvel_pb2.CharacterResponse(characters=characters)

    def _build_response_from_cache(self, cached_response):
        """
        Convert cached data into a gRPC response format.
        """
        return self._build_response_from_api(cached_response)

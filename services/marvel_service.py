"""
Marvel service for fetching Marvel characters.
"""

# pylint: disable=no-member
import logging

from marvel.api import get_marvel_characters
from marvel.proto import marvel_pb2
from marvel.proto import marvel_pb2_grpc

from utils.cache import Cache, generate_cache_key

logger = logging.getLogger(__name__)

# Initialize the custom cache
cache = Cache(maxsize=1000, ttl=300)


class MarvelService(marvel_pb2_grpc.MarvelServiceServicer):
    """
    Marvel service for fetching Marvel characters.
    """

    def GetCharacters(self, request, context):
        """
        Fetch Marvel characters based on the gRPC request parameters.
        Uses caching to avoid redundant API calls.
        """
        try:
            # Prepare query parameters from the gRPC request
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

            # Generate a cache key based on the parameters
            cache_key = generate_cache_key(query_params)

            # Check the cache for a pre-existing response
            cached_response = cache.get(cache_key)
            if cached_response:
                return self._build_response_from_cache(cached_response)

            # Fetch data from the Marvel API
            api_response = get_marvel_characters(**query_params)

            # Cache the response
            cache.set(cache_key, api_response)

            # Build the gRPC response
            return self._build_response_from_api(api_response)

        except Exception as e:
            context.set_details(str(e))
            context.set_code(marvel_pb2.StatusCode.INTERNAL)
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

    def GetCacheStats(self, request, context):
        """
        Expose cache statistics via gRPC.
        """
        stats = cache.stats()
        return marvel_pb2.CacheStatsResponse(
            hits=stats["hits"],
            misses=stats["misses"],
            total_requests=stats["total_requests"],
            hit_ratio=stats["hit_ratio"],
        )

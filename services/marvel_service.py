"""
Marvel service for fetching Marvel characters.
"""

import asyncio
import logging
import grpc

from marvel.api import get_marvel_characters
from marvel.proto import marvel_pb2
from marvel.proto import marvel_pb2_grpc

from utils.cache import Cache

logger = logging.getLogger(__name__)

# Initialize the custom cache
cache = Cache(maxsize=1000, ttl=300)


class MarvelService(marvel_pb2_grpc.MarvelServiceServicer):
    """
    A service for fetching Marvel characters.
    """

    def GetCharacters(self, request: marvel_pb2.CharacterRequest, context):
        cache_key = f"{request.query}:{request.offset}:{request.limit}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return cached_result

        try:
            api_response = asyncio.run(
                get_marvel_characters(
                    query=request.query, offset=request.offset, limit=request.limit
                )
            )

            data = api_response.get("data", {})

            characters = []

            for result in data.get("results", []):
                characters.append(
                    marvel_pb2.Character(
                        id=result.get("id", 0),
                        name=result.get("name", ""),
                        description=result.get("description", ""),
                        modified=result.get("modified", ""),
                        resourceURI=result.get("resourceURI", ""),
                        urls=[
                            marvel_pb2.Url(type=url["type"], url=url["url"])
                            for url in result.get("urls", [])
                        ],
                        thumbnail=marvel_pb2.Image(
                            path=result["thumbnail"]["path"],
                            extension=result["thumbnail"]["extension"],
                        ),
                        comics=self._build_resource_list(result.get("comics", {})),
                        stories=self._build_resource_list(result.get("stories", {})),
                        events=self._build_resource_list(result.get("events", {})),
                        series=self._build_resource_list(result.get("series", {})),
                    )
                )

            response = marvel_pb2.CharacterResponse(
                code=api_response.get("code", 0),
                status=api_response.get("status", ""),
                copyright=api_response.get("copyright", ""),
                attributionText=api_response.get("attributionText", ""),
                attributionHTML=api_response.get("attributionHTML", ""),
                etag=api_response.get("etag", ""),
                offset=data.get("offset", 0),
                limit=data.get("limit", 0),
                total=data.get("total", 0),
                count=data.get("count", 0),
                characters=characters,
            )

            # Cache the result
            cache.set(cache_key, response)

            return response

        except Exception as e:
            logger.error("Error fetching characters: %s", e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return marvel_pb2.CharacterResponse()

    def _build_resource_list(self, resource_data):
        """Helper to build resource lists (e.g., comics, stories)."""
        return marvel_pb2.ResourceList(
            available=resource_data.get("available", 0),
            returned=resource_data.get("returned", 0),
            collectionURI=resource_data.get("collectionURI", ""),
            comics=[
                marvel_pb2.ComicSummary(
                    resourceURI=item.get("resourceURI", ""), name=item.get("name", "")
                )
                for item in resource_data.get("items", [])
            ],
        )

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

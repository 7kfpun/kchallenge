"""
Marvel service for fetching Marvel characters.
"""

import logging
import grpc

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

    async def GetCharacters(
        self, request: marvel_pb2.CharacterRequest, context: grpc.ServicerContext
    ) -> marvel_pb2.CharacterResponse:
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

        except TimeoutError as e:
            logger.error("[MarvelService] TimeoutError fetching characters: %s", e)
            context.set_code(context.Code.INTERNAL)
            context.set_details("Failed to fetch characters.")
            return marvel_pb2.CharacterResponse()

        except Exception as e:
            logger.error("[MarvelService] Error fetching characters: %s", e)
            context.set_code(context.Code.INTERNAL)
            context.set_details("Failed to fetch characters.")
            return marvel_pb2.CharacterResponse()

    def _build_response_from_api(self, api_response: dict):
        """
        Convert the Marvel API response into a gRPC response format.
        """

        def _build_resource_list(api_resource, resource_type):
            items = []
            if resource_type == "comics":
                items = [
                    marvel_pb2.ComicSummary(
                        resourceURI=item["resourceURI"], name=item["name"]
                    )
                    for item in api_resource.get("items", [])
                ]
            elif resource_type == "stories":
                items = [
                    marvel_pb2.StorySummary(
                        resourceURI=item["resourceURI"],
                        name=item["name"],
                        type=item.get("type", ""),
                    )
                    for item in api_resource.get("items", [])
                ]
            elif resource_type == "events":
                items = [
                    marvel_pb2.EventSummary(
                        resourceURI=item["resourceURI"], name=item["name"]
                    )
                    for item in api_resource.get("items", [])
                ]
            elif resource_type == "series":
                items = [
                    marvel_pb2.SeriesSummary(
                        resourceURI=item["resourceURI"], name=item["name"]
                    )
                    for item in api_resource.get("items", [])
                ]

            return marvel_pb2.ResourceList(
                available=api_resource.get("available", 0),
                returned=api_resource.get("returned", 0),
                collectionURI=api_resource.get("collectionURI", ""),
                comics=items if resource_type == "comics" else [],
                stories=items if resource_type == "stories" else [],
                events=items if resource_type == "events" else [],
                series=items if resource_type == "series" else [],
            )

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
                comics=_build_resource_list(result.get("comics", {}), "comics"),
                stories=_build_resource_list(result.get("stories", {}), "stories"),
                events=_build_resource_list(result.get("events", {}), "events"),
                series=_build_resource_list(result.get("series", {}), "series"),
            )
            for result in api_response.get("data", {}).get("results", [])
        ]

        return marvel_pb2.CharacterResponse(
            code=api_response.get("code", 0),
            status=api_response.get("status", ""),
            copyright=api_response.get("copyright", ""),
            attributionText=api_response.get("attributionText", ""),
            attributionHTML=api_response.get("attributionHTML", ""),
            etag=api_response.get("etag", ""),
            offset=api_response.get("data", {}).get("offset", 0),
            limit=api_response.get("data", {}).get("limit", 0),
            total=api_response.get("data", {}).get("total", 0),
            count=api_response.get("data", {}).get("count", 0),
            characters=characters,
        )

    def _build_response_from_cache(self, cached_response: dict):
        """
        Convert cached data into a gRPC response format.
        """
        return self._build_response_from_api(cached_response)

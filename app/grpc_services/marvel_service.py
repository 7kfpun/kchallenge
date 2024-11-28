"""
Marvel service for fetching Marvel characters with streaming updates.
"""

# pylint: disable=no-member,broad-exception-caught
import asyncio
import logging

from app.api.marvel_api import get_marvel_characters
from app.cache import cache
from app.grpc_services.proto import marvel_pb2
from app.grpc_services.proto import marvel_pb2_grpc
from app.utils.cache import generate_cache_key
from app.utils.character_response_utils import build_character_response
from app.utils.stream_manager import StreamManager

stream_manager = StreamManager()

logger = logging.getLogger(__name__)


class MarvelService(marvel_pb2_grpc.MarvelServiceServicer):
    """
    Marvel service for fetching Marvel characters with streaming updates.
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
            return build_character_response(cached_response)

        try:
            response = await get_marvel_characters(headers=headers, **query_params)

            if response.status_code == 304:  # Not Modified
                cached_data = cache.get(cache_key)
                return build_character_response(cached_data)

            response_data = response.json()
            new_etag = response.headers.get("Etag")
            cache.set(cache_key, response_data, etag=new_etag)

            # Notify all subscribers about the update
            asyncio.create_task(
                self._notify_subscribers(
                    cache_key, build_character_response(response_data)
                )
            )

            return build_character_response(response_data)

        except Exception as e:
            logger.error("[MarvelService] Error fetching characters: %s", e)
            context.set_code(context.Code.INTERNAL)
            context.set_details("Failed to fetch characters.")
            return marvel_pb2.CharacterResponse()

    async def StreamUpdates(self, request, context):
        """
        Stream updates for a specific query.
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

        try:
            # Subscribe the client to updates for this query
            stream_manager.subscribe(cache_key, context)
            logger.info("[StreamUpdates] Client subscribed for key: %s", cache_key)

            while True:
                await asyncio.sleep(10)  # Keep the stream alive

        except asyncio.CancelledError:
            logger.info("[StreamUpdates] Client unsubscribed for key: %s", cache_key)
            stream_manager.unsubscribe(cache_key, context)

        except Exception as e:
            logger.error("[StreamUpdates] Error handling stream: %s", e)
            context.set_code(context.Code.INTERNAL)
            context.set_details("Failed to stream updates.")

    async def _notify_subscribers(self, cache_key, character_response):
        """
        Notify all subscribers about an updated character response.
        :param character_response: The updated CharacterResponse object.
        """
        try:
            await stream_manager.broadcast_if_subscribed(cache_key, character_response)
        except Exception as e:
            logger.error("[MarvelService] Failed to notify subscribers: %s", e)

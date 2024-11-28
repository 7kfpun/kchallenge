"""
MarvelTask: Handles Marvel API cache updates.
"""

# pylint: disable=broad-exception-caught
import json
import logging
import urllib.parse

from app.api.cache import cache
from app.api.marvel_api import get_marvel_characters
from app.grpc_services.proto import marvel_pb2
from app.utils.character_response_utils import build_character_response
from app.workers.broker import broker
from app.workers.stream_manager import StreamManager

logger = logging.getLogger(__name__)
stream_manager = StreamManager()


@broker.task
async def enqueue_marvel_tasks():
    """
    Enqueue all Marvel-related cache keys into the Taskiq queue.
    """
    try:
        # Fetch all cache keys
        all_keys = list(cache.store.keys())
        logger.debug("[MarvelTask] Found %d cache keys to enqueue.", len(all_keys))

        # Enqueue tasks for each key
        for cache_key in all_keys:
            await update_marvel_cache.kiq(cache_key)
            logger.info("[MarvelTask] Task enqueued for key: %s", cache_key)

    except Exception as e:
        logger.error("[MarvelTask] Failed to enqueue Marvel tasks: %s", e)


@broker.task
async def update_marvel_cache(cache_key: str):
    """
    Update cache for a specific Marvel API key and stream updates to interested clients.
    :param cache_key: The cache key to update.
    """
    try:
        query_params = _extract_query_params_from_key(cache_key)
        if not query_params:
            logger.warning(
                "[MarvelTask] No query parameters found for key: %s", cache_key
            )
            return

        cached_etag = cache.get_etag(cache_key)
        headers = {"If-None-Match": cached_etag} if cached_etag else {}

        response = await get_marvel_characters(headers=headers, **query_params)

        if response.status_code == 304:
            logger.info("[MarvelTask] Cache entry is up to date for key: %s", cache_key)
            return

        response.raise_for_status()
        response_data = response.json()
        if "data" not in response_data or "results" not in response_data["data"]:
            logger.error(
                "[MarvelTask] Unexpected response format for key: %s", cache_key
            )
            return

        new_etag = response.headers.get("Etag")
        cache.set(cache_key, response_data, etag=new_etag)
        logger.info("[MarvelTask] Updated cache for key: %s", cache_key)

        # Build a CharacterResponse from the updated data
        character_response = build_character_response(response_data)

        # Broadcast updates only to interested clients
        await stream_manager.broadcast_if_subscribed(cache_key, character_response)

    except Exception as e:
        logger.error("[MarvelTask] Failed to process task for key %s: %s", cache_key, e)


def _extract_query_params_from_key(cache_key: str) -> dict:
    """
    Extract query parameters from the cache key.
    :param cache_key: The cache key string.
    :return: Dictionary of query parameters.
    """
    try:
        if cache_key.startswith("{") and cache_key.endswith("}"):
            return json.loads(cache_key)

        # If the cache key is in URL-encoded format
        parsed_params = urllib.parse.parse_qs(cache_key)
        query_params = {k: v[0] if len(v) == 1 else v for k, v in parsed_params.items()}
        return query_params
    except Exception as e:
        logger.error(
            "[MarvelTask] Failed to parse query params from key %s: %s",
            cache_key,
            e,
        )
    return {}

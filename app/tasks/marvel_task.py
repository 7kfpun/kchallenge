"""
MarvelTask: Handles Marvel API cache updates.
"""

# pylint: disable=broad-exception-caught
import logging
import json

from app.api.marvel_api import get_marvel_characters
from app.api.cache import cache
from app.workers.broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def update_marvel_cache(cache_key: str):
    """
    Update cache for a specific Marvel API key.
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
        updated_characters = response_data["data"]["results"]
        cache.set(cache_key, updated_characters, etag=new_etag)
        logger.info("[MarvelTask] Updated cache for key: %s", cache_key)

    except Exception as e:
        logger.error("[MarvelTask] Failed to process task for key %s: %s", cache_key, e)


@broker.task
async def enqueue_marvel_tasks():
    """
    Enqueue all Marvel-related cache keys into the Taskiq queue.
    """
    all_keys = list(cache.store.keys())
    for cache_key in all_keys:
        await update_marvel_cache.kiq(cache_key)
        logger.info("[MarvelTask] Task enqueued for key: %s", cache_key)


def _extract_query_params_from_key(cache_key: str) -> dict:
    """
    Extract query parameters from the cache key.
    :param cache_key: The cache key string.
    :return: Dictionary of query parameters.
    """
    try:
        if cache_key.startswith("{") and cache_key.endswith("}"):
            return json.loads(cache_key)

        return dict(param.split("=") for param in cache_key.split("&") if "=" in param)
    except Exception as e:
        logger.error(
            "[MarvelTask] Failed to parse query params from key %s: %s",
            cache_key,
            e,
        )
    return {}

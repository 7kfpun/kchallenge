"""
Task for updating Marvel API cache entries.
"""

# pylint: disable=broad-exception-caught
import logging
import json
from marvel.api import get_marvel_characters
from marvel.cache import cache

logger = logging.getLogger(__name__)


class MarvelTask:
    """
    Task for updating Marvel API cache entries.
    """

    @staticmethod
    def get_tasks():
        """
        Get all keys (tasks) from the cache.
        This method is required by the Worker.
        """
        return cache.store.keys()

    @staticmethod
    def execute_task(cache_key):
        """
        Execute a single task to check and update the cache for the given key.
        """
        try:
            cached_etag = cache.get_etag(cache_key)
            headers = {}
            if cached_etag:
                headers["If-None-Match"] = cached_etag

            query_params = MarvelTask._extract_query_params_from_key(cache_key)
            response = get_marvel_characters(headers=headers, **query_params)

            if response.status_code == 304:
                logger.info("[Task] Cache entry is up to date for key: %s", cache_key)
                return

            response.raise_for_status()
            new_etag = response.headers.get("Etag")
            updated_characters = response.json().get("data", {}).get("results", [])
            cache.set(cache_key, updated_characters, etag=new_etag)
            logger.info("[Task] Updated cache for key: %s", cache_key)

        except Exception as e:
            logger.error("[Task] Failed to update cache for key %s: %s", cache_key, e)
            raise

    @staticmethod
    def _extract_query_params_from_key(cache_key):
        """
        Extract query parameters from the cache key.
        """
        try:
            key_parts = cache_key.split(":", 1)
            if len(key_parts) == 2:
                return json.loads(key_parts[1])
        except json.JSONDecodeError as e:
            logger.error("[Task] Failed to parse query params from cache key: %s", e)
        return {}

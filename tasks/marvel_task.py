"""
MarvelTask: Handles Marvel API cache updates.
"""

import logging
from marvel.api import get_marvel_characters
from marvel.cache import cache

logger = logging.getLogger(__name__)


class MarvelTask:
    """
    Handles tasks related to Marvel API and cache updates.
    """

    @staticmethod
    def enqueue_tasks(task_queue):
        """
        Enqueue all Marvel-related cache keys into the shared task queue.
        :param task_queue: The shared task queue managed by WorkerManager.
        """
        logger.info("[MarvelTask] Enqueuing tasks...")
        all_keys = list(cache.store.keys())
        for cache_key in all_keys:
            task = {"task_name": "marvel_task", "params": {"cache_key": cache_key}}
            if not task_queue.full():
                task_queue.put(task)
                logger.info("[MarvelTask] Task enqueued: %s", task)

    @staticmethod
    def execute_task(task):
        """
        Execute a single Marvel task to update the cache.
        :param task: A dictionary containing the task name and parameters.
        """
        try:
            params = task["params"]
            cache_key = params["cache_key"]

            # Extract query parameters from the cache key
            query_params = MarvelTask._extract_query_params_from_key(cache_key)
            if not query_params:
                logger.warning(
                    "[MarvelTask] No query parameters found for key: %s", cache_key
                )
                return

            # Retrieve the ETag for conditional requests
            cached_etag = cache.get_etag(cache_key)
            headers = {"If-None-Match": cached_etag} if cached_etag else {}

            # Fetch data from the Marvel API
            response = get_marvel_characters(headers=headers, **query_params)

            if response.status_code == 304:
                logger.info(
                    "[MarvelTask] Cache entry is up to date for key: %s", cache_key
                )
                return

            response.raise_for_status()

            # Update the cache with new data and ETag
            new_etag = response.headers.get("Etag")
            updated_characters = response.json().get("data", {}).get("results", [])
            cache.set(cache_key, updated_characters, etag=new_etag)
            logger.info("[MarvelTask] Updated cache for key: %s", cache_key)

        except Exception as e:
            logger.error("[MarvelTask] Failed to process task: %s", e)

    @staticmethod
    def _extract_query_params_from_key(cache_key):
        """
        Extract query parameters from the cache key.
        :param cache_key: The cache key string.
        :return: Dictionary of query parameters.
        """
        # Assume cache keys are in JSON format or raw query strings
        try:
            if cache_key.startswith("{") and cache_key.endswith("}"):
                return json.loads(cache_key)
            else:
                return dict(
                    param.split("=") for param in cache_key.split("&") if "=" in param
                )
        except Exception as e:
            logger.error(
                "[MarvelTask] Failed to parse query params from key %s: %s",
                cache_key,
                e,
            )
        return {}

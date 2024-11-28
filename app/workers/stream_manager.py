"""
StreamManager: Manages subscriptions and broadcasting updates to clients.
"""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class StreamManager:
    def __init__(self):
        self.subscriptions = defaultdict(set)

    def subscribe(self, cache_key, context):
        """
        Add a client context to the subscription list for the given cache key.
        """
        self.subscriptions[cache_key].add(context)
        logger.info("[StreamManager] Client subscribed to key: %s", cache_key)

    def unsubscribe(self, cache_key, context):
        """
        Remove a client context from the subscription list for the given cache key.
        """
        if context in self.subscriptions[cache_key]:
            self.subscriptions[cache_key].remove(context)
            logger.info("[StreamManager] Client unsubscribed from key: %s", cache_key)

        if not self.subscriptions[cache_key]:
            del self.subscriptions[cache_key]

    async def broadcast_if_subscribed(self, cache_key, response):
        """
        Broadcast updates to all subscribed clients for the given cache key.
        """
        if cache_key not in self.subscriptions:
            logger.info("[StreamManager] No subscribers for key: %s", cache_key)
            return

        clients = list(self.subscriptions[cache_key])
        for client in clients:
            try:
                await client.write(response)
                logger.info("[StreamManager] Update broadcasted to key: %s", cache_key)
            except Exception as e:
                logger.error("[StreamManager] Failed to broadcast update: %s", e)
                self.unsubscribe(cache_key, client)

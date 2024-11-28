"""
StreamManager: Manages subscriptions and broadcasting updates to clients.
"""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class StreamManager:
    """
    StreamManager: Manages subscriptions and broadcasting updates to clients.
    """

    def __init__(self):
        self.subscriptions = defaultdict(set)

    def subscribe(self, topic, context):
        """
        Add a client context to the subscription list for the given topic.
        """
        self.subscriptions[topic].add(context)
        logger.info("[StreamManager] Client subscribed to key: %s", topic)

    def unsubscribe(self, topic, context):
        """
        Remove a client context from the subscription list for the given topic.
        """
        if context in self.subscriptions[topic]:
            self.subscriptions[topic].remove(context)
            logger.info("[StreamManager] Client unsubscribed from key: %s", topic)

        if not self.subscriptions[topic]:
            del self.subscriptions[topic]

    async def broadcast_if_subscribed(self, topic, response):
        """
        Broadcast updates to all subscribed clients for the given topic.
        """
        if topic not in self.subscriptions:
            logger.info("[StreamManager] No subscribers for key: %s", topic)
            return

        clients = list(self.subscriptions[topic])
        for client in clients:
            try:
                await client.write(response)
                logger.info("[StreamManager] Update broadcasted to key: %s", topic)
            except Exception as e:
                logger.error("[StreamManager] Failed to broadcast update: %s", e)
                self.unsubscribe(topic, client)

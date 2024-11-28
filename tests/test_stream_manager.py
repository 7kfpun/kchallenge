"""
Test StreamManager.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock
from app.utils.stream_manager import StreamManager


class TestStreamManager(unittest.TestCase):
    """
    Test StreamManager.
    """

    def setUp(self):
        self.stream_manager = StreamManager()
        self.topic = "test_key"
        self.mock_context = AsyncMock()

    def test_subscribe(self):
        """
        Test that a client can subscribe to a cache key.
        """
        self.stream_manager.subscribe(self.topic, self.mock_context)
        self.assertIn(self.topic, self.stream_manager.subscriptions)
        self.assertIn(self.mock_context, self.stream_manager.subscriptions[self.topic])

    def test_unsubscribe(self):
        """
        Test that a client can unsubscribe from a cache key.
        """
        # Subscribe first
        self.stream_manager.subscribe(self.topic, self.mock_context)

        # Unsubscribe and verify
        self.stream_manager.unsubscribe(self.topic, self.mock_context)
        self.assertNotIn(
            self.mock_context,
            self.stream_manager.subscriptions.get(self.topic, set()),
        )

    def test_unsubscribe_last_client(self):
        """
        Test that the cache key is removed when the last client unsubscribes.
        """
        self.stream_manager.subscribe(self.topic, self.mock_context)
        self.stream_manager.unsubscribe(self.topic, self.mock_context)
        self.assertNotIn(self.topic, self.stream_manager.subscriptions)

    async def test_broadcast_if_subscribed(self):
        """
        Test that updates are broadcasted to all subscribed clients.
        """
        # Mock response
        mock_response = MagicMock()

        # Subscribe a client
        self.stream_manager.subscribe(self.topic, self.mock_context)

        # Broadcast the response
        await self.stream_manager.broadcast_if_subscribed(self.topic, mock_response)

        # Verify that the client received the update
        self.mock_context.write.assert_awaited_once_with(mock_response)

    async def test_broadcast_to_multiple_clients(self):
        """
        Test broadcasting updates to multiple clients.
        """
        # Mock response
        mock_response = MagicMock()

        # Subscribe multiple clients
        mock_context_1 = AsyncMock()
        mock_context_2 = AsyncMock()
        self.stream_manager.subscribe(self.topic, mock_context_1)
        self.stream_manager.subscribe(self.topic, mock_context_2)

        # Broadcast the response
        await self.stream_manager.broadcast_if_subscribed(self.topic, mock_response)

        # Verify both clients received the update
        mock_context_1.write.assert_awaited_once_with(mock_response)
        mock_context_2.write.assert_awaited_once_with(mock_response)

    async def test_broadcast_with_unsubscribed_client(self):
        """
        Test that unsubscribed clients do not receive updates.
        """
        # Mock response
        mock_response = MagicMock()

        # Subscribe and then unsubscribe a client
        self.stream_manager.subscribe(self.topic, self.mock_context)
        self.stream_manager.unsubscribe(self.topic, self.mock_context)

        # Broadcast the response
        await self.stream_manager.broadcast_if_subscribed(self.topic, mock_response)

        # Verify unsubscribed client did not receive the update
        self.mock_context.write.assert_not_awaited()

    async def test_broadcast_with_failed_client(self):
        """
        Test that failed clients are unsubscribed and do not block broadcasting.
        """
        # Mock response
        mock_response = MagicMock()

        # Subscribe a failing client
        failing_context = AsyncMock()
        failing_context.write.side_effect = Exception("Broadcast failed")
        self.stream_manager.subscribe(self.topic, failing_context)

        # Broadcast the response
        await self.stream_manager.broadcast_if_subscribed(self.topic, mock_response)

        # Verify that the client is unsubscribed
        self.assertNotIn(
            failing_context,
            self.stream_manager.subscriptions.get(self.topic, set()),
        )

    def tearDown(self):
        self.stream_manager = None

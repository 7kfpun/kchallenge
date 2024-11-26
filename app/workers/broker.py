"""
Taskiq worker manager.
"""

import logging

from taskiq import InMemoryBroker

# Configure logger
logger = logging.getLogger(__name__)

# Initialize an in-memory broker
broker = InMemoryBroker()

"""
Marvel cache for storing API responses.
"""

from utils.cache import Cache

# Initialize the custom cache
cache = Cache(maxsize=1000, ttl=300)

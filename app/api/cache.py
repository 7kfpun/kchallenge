"""
Marvel cache for storing API responses.
"""

import os

from dotenv import load_dotenv
from app.utils.cache import Cache

load_dotenv()

CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "1000"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# Initialize the custom cache
cache = Cache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

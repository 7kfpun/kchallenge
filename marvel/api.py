"""
Marvel API module.
"""

import hashlib
import time
from urllib.parse import urlencode
import os
import httpx

import dotenv

dotenv.load_dotenv()

MARVEL_API_BASE_URL = "https://gateway.marvel.com/v1/public/characters"
MARVEL_API_PUBLIC_KEY = os.getenv("MARVEL_API_PUBLIC_KEY")
MARVEL_API_PRIVATE_KEY = os.getenv("MARVEL_API_PRIVATE_KEY")


def generate_hash(ts: str, private_key: str, public_key: str) -> str:
    """
    Generate a hash for the Marvel API request.
    """
    data = f"{ts}{private_key}{public_key}"
    return hashlib.md5(data.encode()).hexdigest()


async def get_marvel_characters(query: str, offset: int, limit: int) -> dict:
    """
    Get Marvel characters.
    """
    ts = str(int(time.time()))
    hash_value = generate_hash(ts, MARVEL_API_PRIVATE_KEY, MARVEL_API_PUBLIC_KEY)

    params = {
        "apikey": MARVEL_API_PUBLIC_KEY,
        "ts": ts,
        "hash": hash_value,
        "nameStartsWith": query,
        "offset": offset,
        "limit": limit,
    }

    url = MARVEL_API_BASE_URL + "?" + urlencode(params)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_marvel_characters("spider", 0, 10)))

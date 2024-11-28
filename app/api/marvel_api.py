"""
Marvel API module (Async Version).
"""

# pylint: disable=too-many-arguments,too-many-locals,broad-exception-caught
import hashlib
import time
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

MARVEL_API_BASE_URL = "https://gateway.marvel.com/v1/public/characters"
MARVEL_API_PUBLIC_KEY = os.getenv("MARVEL_API_PUBLIC_KEY")
MARVEL_API_PRIVATE_KEY = os.getenv("MARVEL_API_PRIVATE_KEY")
MARVEL_API_TIMEOUT = float(os.getenv("MARVEL_API_TIMEOUT", "10"))


def generate_hash(ts: str, private_key: str, public_key: str) -> str:
    """
    Generate a hash for the Marvel API request.
    """
    data = f"{ts}{private_key}{public_key}"
    return hashlib.md5(data.encode()).hexdigest()


async def get_marvel_characters(
    name: str = None,
    name_starts_with: str = None,
    modified_since: str = None,
    comics: list[int] = None,
    series: list[int] = None,
    events: list[int] = None,
    stories: list[int] = None,
    order_by: str = None,
    limit: int = 20,
    offset: int = 0,
    headers: dict = None,
):
    """
    Asynchronously fetch Marvel characters from the API.
    """
    ts = str(int(time.time()))
    hash_value = generate_hash(ts, MARVEL_API_PRIVATE_KEY, MARVEL_API_PUBLIC_KEY)

    # Build query parameters dynamically
    params = {
        "apikey": MARVEL_API_PUBLIC_KEY,
        "ts": ts,
        "hash": hash_value,
        "limit": limit,
        "offset": offset,
    }

    # Add optional parameters if provided
    if name:
        params["name"] = name
    if name_starts_with:
        params["nameStartsWith"] = name_starts_with
    if modified_since:
        params["modifiedSince"] = modified_since
    if comics:
        params["comics"] = ",".join(map(str, comics))
    if series:
        params["series"] = ",".join(map(str, series))
    if events:
        params["events"] = ",".join(map(str, events))
    if stories:
        params["stories"] = ",".join(map(str, stories))
    if order_by:
        params["orderBy"] = order_by

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                MARVEL_API_BASE_URL,
                params=params,
                headers=headers or {},
                timeout=MARVEL_API_TIMEOUT,
            )
            response.raise_for_status()
            return response
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 304:
            return e.response  # Return the 304 response for Etag handling
        raise
    except Exception as e:
        raise RuntimeError(f"Error fetching Marvel characters: {e}") from e

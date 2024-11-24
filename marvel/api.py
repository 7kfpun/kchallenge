"""
Marvel API module.
"""

# pylint: disable=too-many-arguments

import hashlib
import os
import time

import dotenv
import httpx

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


def get_marvel_characters(
    headers: dict = None,
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
):
    """
    Fetch Marvel characters from the API with support for all available query parameters.
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
        params["comics"] = (
            ",".join(map(str, comics)) if isinstance(comics, list) else comics
        )
    if series:
        params["series"] = (
            ",".join(map(str, series)) if isinstance(series, list) else series
        )
    if events:
        params["events"] = (
            ",".join(map(str, events)) if isinstance(events, list) else events
        )
    if stories:
        params["stories"] = (
            ",".join(map(str, stories)) if isinstance(stories, list) else stories
        )
    if order_by:
        params["orderBy"] = order_by

    # Make the request
    response = httpx.get(MARVEL_API_BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

"""Addresses to coordinates (OpenStreetMap Nominatim) and distances between them."""

import math
from functools import lru_cache

import httpx

from tusk_mcp.core.config import settings

Point = tuple[float, float]


@lru_cache(maxsize=1024)
def geocode(text: str) -> Point | None:
    """Best guess at where `text` (an address or area in Nigeria) is. None when unknown or disabled."""
    text = " ".join(text.split())
    if not text or not settings.GEOCODER_URL:
        return None
    try:
        response = httpx.get(
            settings.GEOCODER_URL,
            params={"q": text, "format": "json", "limit": 1, "countrycodes": "ng"},
            headers={"User-Agent": settings.GEOCODER_USER_AGENT},
            timeout=4,
        )
        response.raise_for_status()
        found = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    return (float(found[0]["lat"]), float(found[0]["lon"])) if found else None


def distance_km(a: Point, b: Point) -> float:
    """Straight-line (haversine) distance."""
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

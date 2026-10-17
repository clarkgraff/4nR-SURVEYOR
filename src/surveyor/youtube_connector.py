"""D6B: official YouTube Data API search connector (metadata only).

An explicitly configured API key is required. No video/media downloading,
transcript extraction, scraping, or autonomous API credential provisioning.
"""
from __future__ import annotations
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .discovery import DiscoveryHit

_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"

def parse_youtube_search(payload: dict) -> list[DiscoveryHit]:
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Invalid YouTube API response")
    found = []
    for item in payload["items"]:
        if not isinstance(item, dict):
            continue
        identifier = item.get("id", {})
        snippet = item.get("snippet", {})
        if not isinstance(identifier, dict) or not isinstance(snippet, dict):
            continue
        kind = identifier.get("kind")
        if kind == "youtube#video":
            value = identifier.get("videoId")
            if not isinstance(value, str) or not value:
                continue
            url = "https://www.youtube.com/watch?v=" + value
            category = "video"
        elif kind == "youtube#channel":
            value = identifier.get("channelId")
            if not isinstance(value, str) or not value:
                continue
            url = "https://www.youtube.com/channel/" + value
            category = "channel"
        else:
            continue
        title = snippet.get("title", "")
        if not isinstance(title, str) or not title.strip():
            continue
        hit = DiscoveryHit(
            provider="youtube", url=url, title=title,
            description=str(snippet.get("description", "")),
            creator=str(snippet.get("channelTitle", "")),
            kind=category,
            published_date=str(snippet.get("publishedAt", "")),
        )
        hit.validate()
        found.append(hit)
    return found

def youtube_connector(*, api_key: str | None = None, timeout: float = 12,
                      opener=None):
    """Return D6A-compatible search callable. API key stays out of results."""
    key = api_key if api_key is not None else os.environ.get("SURVEYOR_YOUTUBE_API_KEY", "")
    if not key or not key.strip():
        raise ValueError("Set SURVEYOR_YOUTUBE_API_KEY for official YouTube discovery")
    if not (1 <= timeout <= 60):
        raise ValueError("Invalid API timeout")
    opener = opener or urlopen

    def search(query: str, limit: int) -> list[DiscoveryHit]:
        if not query.strip() or not 1 <= limit <= 50:
            raise ValueError("Invalid YouTube query or result limit")
        params = {"part": "snippet", "q": query, "type": "video,channel",
                  "maxResults": str(limit), "key": key}
        request = Request(_ENDPOINT + "?" + urlencode(params),
                          headers={"Accept": "application/json", "User-Agent": "4nR-SURVEYOR/0.6"})
        with opener(request, timeout=timeout) as response:
            if response.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                raise ValueError("Unexpected YouTube response content type")
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("YouTube discovery response exceeds 1 MiB")
            payload = json.loads(raw.decode("utf-8-sig"))
        return parse_youtube_search(payload)[:limit]
    return search

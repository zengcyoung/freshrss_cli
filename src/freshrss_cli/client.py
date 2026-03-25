"""FreshRSS API client helpers — connection and data operations, no CLI logic."""

from __future__ import annotations

import html
import re
from typing import Any

from freshrss_api import FreshRSSAPI, Item


def connect(url: str, username: str, password: str) -> FreshRSSAPI:
    """Create and return an authenticated FreshRSS API client."""
    return FreshRSSAPI(host=url, username=username, password=password)


def _item_to_dict(item: Item, feed_map: dict[int, str] | None = None) -> dict[str, Any]:
    """Convert an Item dataclass to a plain dict."""
    excerpt = _extract_excerpt(item.html)
    return {
        "id": str(item.id),
        "feed_id": str(item.feed_id),
        "feed_name": feed_map.get(item.feed_id, f"feed:{item.feed_id}") if feed_map else f"feed:{item.feed_id}",
        "title": item.title or "(no title)",
        "url": item.url or "",
        "is_read": item.is_read,
        "is_saved": item.is_saved,
        "created_on_time": item.created_on_time,
        "excerpt": excerpt,
    }


def _extract_excerpt(html_content: str, max_chars: int = 200) -> str:
    """Extract a short plain-text excerpt from HTML."""
    if not html_content:
        return ""
    # Strip tags
    text = re.sub(r"<[^>]+>", " ", html_content)
    # Decode entities
    text = html.unescape(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def get_feeds(client: FreshRSSAPI) -> list[dict[str, Any]]:
    """Return list of feed dicts with name, url, id, unread_count."""
    data = client.get_feeds()
    feeds = data.get("feeds", [])
    feeds_groups = data.get("feeds_groups", [])

    # Build unread map from groups data isn't available directly; use favicons_ids workaround
    # unread counts come from the feeds list itself
    result = []
    for f in feeds:
        result.append({
            "id": str(f.get("id", "")),
            "name": f.get("title", "(no name)"),
            "url": f.get("url", ""),
            "site_url": f.get("site_url", ""),
            "unread_count": f.get("unread_count", 0),
        })
    return result


def _build_feed_map(client: FreshRSSAPI) -> dict[int, str]:
    """Build {feed_id: feed_name} mapping."""
    feeds = get_feeds(client)
    return {int(f["id"]): f["name"] for f in feeds}


def get_items(
    client: FreshRSSAPI,
    feed_id: str | None = None,
    unread_only: bool = False,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return list of item dicts, optionally filtered by feed or unread status."""
    feed_map = _build_feed_map(client)

    if unread_only:
        items = client.get_unreads()
    else:
        # Fever API doesn't support general item listing without date range easily.
        # Use unread + saved, or just unread if no filter. For general listing, use recent unreads.
        items = client.get_unreads()

    if feed_id is not None:
        items = [i for i in items if str(i.feed_id) == str(feed_id)]

    items = items[:limit]
    return [_item_to_dict(i, feed_map) for i in items]


def mark_read(client: FreshRSSAPI, item_ids: list[str]) -> None:
    """Mark items as read."""
    for item_id in item_ids:
        client.set_mark(as_="read", id=int(item_id))


def mark_unread(client: FreshRSSAPI, item_ids: list[str]) -> None:
    """Mark items as unread — note: Fever API does not natively support unread marking.
    This will attempt a workaround but may not work on all FreshRSS versions."""
    # Fever API limitation: set_mark does not support 'unread'
    # We'll try calling the internal _call directly
    for item_id in item_ids:
        try:
            client._call(mark="item", as_="unread", id=int(item_id))
        except Exception as exc:
            raise RuntimeError(
                f"Could not mark {item_id} as unread: {exc}. "
                "The Fever API may not support this operation."
            ) from exc


def save_item(client: FreshRSSAPI, item_ids: list[str]) -> None:
    """Save/star items."""
    for item_id in item_ids:
        client.set_mark(as_="saved", id=int(item_id))


def get_digest(client: FreshRSSAPI, limit: int = 20) -> list[dict[str, Any]]:
    """Fetch top unread items formatted for AI morning digest."""
    feed_map = _build_feed_map(client)
    items = client.get_unreads()
    items = items[:limit]
    result = []
    for item in items:
        result.append({
            "id": str(item.id),
            "title": item.title or "(no title)",
            "feed_name": feed_map.get(item.feed_id, f"feed:{item.feed_id}"),
            "url": item.url or "",
            "excerpt": _extract_excerpt(item.html, max_chars=300),
        })
    return result

"""Listing-page extraction (starter implementation)."""

from typing import Any


def fetch_listing_items(_page: Any = None) -> list[dict[str, str]]:
    """
    Return starter listing data.

    Replace this with real listing-page selectors once target site is finalized.
    """
    return [
        {"id": "demo-1", "title": "Sample Item 1", "url": "https://example.com/item/1"},
        {"id": "demo-2", "title": "Sample Item 2", "url": "https://example.com/item/2"},
    ]

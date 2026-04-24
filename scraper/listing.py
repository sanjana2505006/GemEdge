"""Listing-page extraction for initial milestone."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger
from requests import RequestException

from scraper.config import settings
from scraper.http import get_with_retry
from scraper.utils import normalize_text, normalize_url, parse_price_value


def _item_id_from_url(item_url: str, idx: int) -> str:
    match = re.search(r"/([^/?#]+)/?$", item_url)
    if match:
        return match.group(1)
    return f"item-{idx}"


def _extract_item(card: Tag, idx: int) -> dict[str, object] | None:
    title_node = card.select_one(settings.title_selector)
    link_node = card.select_one(settings.link_selector)
    price_node = card.select_one(settings.price_selector)

    if link_node is None or not link_node.get("href"):
        return None

    title = normalize_text(title_node.get_text(strip=True) if title_node else "")
    item_url = normalize_url(settings.base_url, str(link_node["href"]))
    price_text = normalize_text(price_node.get_text(strip=True) if price_node else "")
    price_value = parse_price_value(price_text)

    return {
        "id": _item_id_from_url(item_url, idx),
        "title": title or "Untitled",
        "url": item_url,
        "price": price_text or "N/A",
        "price_value": price_value,
    }


def _build_page_url(page_num: int) -> str:
    base_listing_url = urljoin(settings.base_url, settings.listing_path)
    separator = "&" if "?" in base_listing_url else "?"
    return f"{base_listing_url}{separator}page={page_num}"


def fetch_listing_items() -> list[dict[str, object]]:
    """Scrape listing pages and return minimal item records."""
    results: list[dict[str, object]] = []
    seen_urls: set[str] = set()

    for page_num in range(1, settings.max_pages + 1):
        page_url = _build_page_url(page_num)
        logger.info("Fetching listing page {}", page_url)

        try:
            response = get_with_retry(page_url)
        except RequestException as exc:
            logger.error("Failed to fetch page {}: {}", page_num, exc)
            break

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.select(settings.item_selector)
        logger.info("Found {} cards on page {}", len(cards), page_num)
        if not cards:
            logger.info("Stopping pagination at page {} (no cards found)", page_num)
            break

        page_new_count = 0
        for idx, card in enumerate(cards, start=1):
            parsed = _extract_item(card, idx)
            if parsed is None:
                continue
            if parsed["url"] in seen_urls:
                continue
            seen_urls.add(parsed["url"])
            results.append(parsed)
            page_new_count += 1

        if page_new_count == 0:
            logger.info(
                "Stopping pagination at page {} (no new unique items)",
                page_num,
            )
            break

    return results

"""Listing-page extraction for initial milestone."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger
from requests import RequestException

from scraper.config import settings
from scraper.utils import normalize_text, normalize_url, parse_price_value
from playwright.sync_api import Page
import asyncio


def _item_id_from_url(item_url: str, idx: int) -> str:
    # Extract the book ID from URLs like http://books.toscrape.com/catalogue/book-name_123/index.html
    match = re.search(r"/([^/]+)_\d+/index\.html$", item_url)
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
    href = str(link_node["href"])
    # Handle relative URLs - books.toscrape.com uses relative paths like ../../catalogue/book-name_123/index.html
    if href.startswith('/'):
        item_url = normalize_url(settings.base_url, href)
    elif href.startswith('../'):
        # Convert relative path to absolute URL
        # ../../catalogue/book-name_123/index.html -> /catalogue/book-name_123/index.html
        clean_href = href.replace('../', '')
        item_url = f"{settings.base_url}/{clean_href}"
    else:
        # Assume it's a relative path from catalogue directory
        item_url = f"{settings.base_url}/catalogue/{href}"
    
    price_text = normalize_text(price_node.get_text(strip=True) if price_node else "")
    price_value = parse_price_value(price_text)
    price_inr = round(price_value * settings.eur_to_inr_rate, 2) if price_value is not None else None
    price_inr_text = f"INR {price_inr:.2f}" if price_inr is not None else "N/A"

    return {
        "id": _item_id_from_url(item_url, idx),
        "title": title or "Untitled",
        "url": item_url,
        "price": price_inr_text,
        "price_inr": price_inr,
    }


def _build_page_url(page_num: int) -> str:
    if page_num == 1:
        return urljoin(settings.base_url, settings.listing_path)
    # For books.toscrape.com format: /catalogue/page-2.html
    base_url = settings.base_url.rstrip('/')
    if page_num > 1:
        return f"{base_url}/catalogue/page-{page_num}.html"
    return f"{base_url}/catalogue/page-1.html"


def fetch_listing_items(page: Page) -> list[dict[str, object]]:
    """Scrape listing pages using Playwright and return minimal item records."""
    results: list[dict[str, object]] = []
    seen_urls: set[str] = set()

    for page_num in range(1, settings.max_pages + 1):
        page_url = _build_page_url(page_num)
        logger.info("Fetching listing page {}", page_url)

        try:
            # Use Playwright to navigate and get content
            logger.info("Navigating to: {}", page_url)
            response = page.goto(page_url, timeout=30000, wait_until="domcontentloaded")
            logger.info("Navigation response status: {}", response.status if response else "No response")
            html_content = page.content()
            logger.info("Page content length: {} chars", len(html_content))
        except Exception as exc:
            logger.error("Failed to fetch page {}: {}", page_num, exc)
            break

        soup = BeautifulSoup(html_content, "lxml")
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

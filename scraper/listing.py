import re
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger
from playwright.sync_api import Page
from tqdm import tqdm

from scraper.config import settings
from scraper.utils import normalize_text, normalize_url, parse_price_value


def _id_from_url(url: str, idx: int) -> str:
    match = re.search(r"/([^/]+)_\d+/index\.html$", url)
    return match.group(1) if match else f"item-{idx}"


def _build_url(href: str) -> str:
    if href.startswith('/'):
        return normalize_url(settings.base_url, href)
    if href.startswith('../'):
        return f"{settings.base_url}/{href.replace('../', '')}"
    return f"{settings.base_url}/catalogue/{href}"


def _extract_item(card: Tag, idx: int) -> dict[str, object] | None:
    title_node = card.select_one(settings.title_selector)
    link_node = card.select_one(settings.link_selector)
    price_node = card.select_one(settings.price_selector)

    if link_node is None or not link_node.get("href"):
        return None

    title = normalize_text(title_node.get("title", "") or title_node.get_text(strip=True) if title_node else "")
    item_url = _build_url(str(link_node["href"]))
    price_text = normalize_text(price_node.get_text(strip=True) if price_node else "")
    price_value = parse_price_value(price_text)
    price_inr = round(price_value * settings.eur_to_inr_rate, 2) if price_value is not None else None

    return {
        "id": _id_from_url(item_url, idx),
        "title": title or "Untitled",
        "seller": "Books to Scrape",
        "url": item_url,
        "price": f"INR {price_inr:.2f}" if price_inr is not None else "N/A",
        "price_inr": price_inr,
        "scraped_date": date.today().isoformat(),
    }


def _page_url(page_num: int) -> str:
    if page_num == 1:
        return urljoin(settings.base_url, settings.listing_path)
    return f"{settings.base_url.rstrip('/')}/catalogue/page-{page_num}.html"


def fetch_listing_items(page: Page) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    seen: set[str] = set()

    for page_num in tqdm(range(1, settings.max_pages + 1), desc="Scraping pages", unit="page"):
        page_url = _page_url(page_num)
        logger.info("Fetching page {}", page_url)

        try:
            page.goto(page_url, timeout=30000, wait_until="domcontentloaded")
            html = page.content()
        except Exception as exc:
            logger.error("Failed page {}: {}", page_num, exc)
            break

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select(settings.item_selector)
        logger.info("Found {} cards on page {}", len(cards), page_num)

        if not cards:
            break

        new_count = 0
        for idx, card in enumerate(cards, start=1):
            item = _extract_item(card, idx)
            if item is None or item["url"] in seen:
                continue
            seen.add(item["url"])
            results.append(item)
            new_count += 1

        if new_count == 0:
            break

    return results

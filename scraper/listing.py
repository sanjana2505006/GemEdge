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
        clean = href.replace('../', '')
        return f"{settings.base_url}/{clean}"
    return f"{settings.base_url}/catalogue/{href}"


def _extract_item(card: Tag, idx: int) -> dict | None:
    title_node = card.select_one(settings.title_selector)
    link_node = card.select_one(settings.link_selector)
    price_node = card.select_one(settings.price_selector)

    if not link_node or not link_node.get("href"):
        return None

    title = ""
    if title_node:
        title = title_node.get("title", "") or title_node.get_text(strip=True)
    title = normalize_text(title)

    item_url = _build_url(str(link_node["href"]))

    price_text = ""
    if price_node:
        price_text = normalize_text(price_node.get_text(strip=True))

    price_value = parse_price_value(price_text)
    if price_value is not None:
        price_inr = round(price_value * settings.eur_to_inr_rate, 2)
        price_str = f"INR {price_inr:.2f}"
    else:
        price_inr = None
        price_str = "N/A"

    return {
        "id": _id_from_url(item_url, idx),
        "title": title if title else "Untitled",
        "seller": "Books to Scrape",
        "url": item_url,
        "price": price_str,
        "price_inr": price_inr,
        "scraped_date": date.today().isoformat(),
    }


def _page_url(page_num: int) -> str:
    if page_num == 1:
        return urljoin(settings.base_url, settings.listing_path)
    base = settings.base_url.rstrip('/')
    return f"{base}/catalogue/page-{page_num}.html"


def fetch_listing_items(page: Page) -> list:
    results = []
    seen = set()

    for page_num in tqdm(range(1, settings.max_pages + 1), desc="pages"):
        url = _page_url(page_num)
        logger.info("fetching {}", url)

        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            html = page.content()
        except Exception as e:
            logger.error("page {} failed: {}", page_num, e)
            break

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select(settings.item_selector)

        if not cards:
            print(f"no cards on page {page_num}, stopping")
            break

        added = 0
        for idx, card in enumerate(cards, start=1):
            item = _extract_item(card, idx)
            if item is None:
                continue
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            results.append(item)
            added += 1

        if added == 0:
            break

    return results

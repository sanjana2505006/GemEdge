"""Detail-page extraction for basic enrichment."""

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from scraper.config import settings
from scraper.utils import normalize_text


def fetch_detail_with_status(item: dict[str, object], page: Page) -> tuple[dict[str, object], bool]:
    """Fetch one detail page using Playwright and return (item, success)."""
    result = {**item, "location": "Unknown", "description": ""}
    url = normalize_text(str(item.get("url", "")))
    if not url:
        return result, False

    try:
        # Use Playwright to navigate and get content
        page.goto(url, timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=5000)
        html_content = page.content()
    except Exception:
        return result, False

    soup = BeautifulSoup(html_content, "lxml")
    location_node = soup.select_one(settings.detail_location_selector)
    description_node = soup.select_one(settings.detail_description_selector)

    if location_node is not None:
        result["location"] = normalize_text(location_node.get_text(strip=True)) or "Unknown"
    if description_node is not None:
        result["description"] = normalize_text(description_node.get_text(strip=True))

    return result, True


def fetch_detail(item: dict[str, object]) -> dict[str, object]:
    """Backward-compatible detail fetch helper."""
    result, _ok = fetch_detail_with_status(item)
    return result

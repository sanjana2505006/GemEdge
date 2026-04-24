"""Detail-page extraction for basic enrichment."""

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from scraper.config import settings
from scraper.utils import normalize_text

# Maps word-based star ratings to numbers
_RATING_MAP = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5"
}


def fetch_detail_with_status(item: dict[str, object], page: Page) -> tuple[dict[str, object], bool]:
    """Fetch one detail page using Playwright and return (item, success)."""
    result = {**item, "category": "Unknown", "rating": "N/A", "availability": "Unknown", "description": ""}
    url = normalize_text(str(item.get("url", "")))
    if not url:
        return result, False

    try:
        page.goto(url, timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=5000)
        html_content = page.content()
    except Exception:
        return result, False

    soup = BeautifulSoup(html_content, "lxml")

    category_node = soup.select_one(settings.detail_category_selector)
    rating_node = soup.select_one(settings.detail_rating_selector)
    availability_node = soup.select_one(settings.detail_availability_selector)
    description_node = soup.select_one(settings.detail_description_selector)

    if category_node is not None:
        result["category"] = normalize_text(category_node.get_text(strip=True)) or "Unknown"

    if rating_node is not None:
        classes = rating_node.get("class", [])
        for cls in classes:
            word = cls.lower()
            if word in _RATING_MAP:
                result["rating"] = f"{_RATING_MAP[word]}/5"
                break

    if availability_node is not None:
        result["availability"] = normalize_text(availability_node.get_text(strip=True)) or "Unknown"

    if description_node is not None:
        result["description"] = normalize_text(description_node.get_text(strip=True))

    return result, True


def fetch_detail(item: dict[str, object], page: Page) -> dict[str, object]:
    """Backward-compatible detail fetch helper."""
    result, _ok = fetch_detail_with_status(item, page)
    return result

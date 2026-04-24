"""Detail-page extraction for basic enrichment."""

from bs4 import BeautifulSoup
from requests import RequestException

from scraper.config import settings
from scraper.http import get_with_retry
from scraper.utils import normalize_text


def fetch_detail_with_status(item: dict[str, object]) -> tuple[dict[str, object], bool]:
    """Fetch one detail page and return (item, success)."""
    result = {**item, "location": "Unknown", "description": ""}
    url = normalize_text(str(item.get("url", "")))
    if not url:
        return result, False

    try:
        response = get_with_retry(url)
    except RequestException:
        return result, False

    soup = BeautifulSoup(response.text, "lxml")
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

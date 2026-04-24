"""Detail-page extraction for basic enrichment."""

from bs4 import BeautifulSoup
from requests import RequestException

from scraper.config import settings
from scraper.http import get_with_retry


def fetch_detail(item: dict[str, str]) -> dict[str, str]:
    """Fetch one detail page and append location/description fields."""
    result = {**item, "location": "Unknown", "description": ""}
    url = item.get("url", "").strip()
    if not url:
        return result

    try:
        response = get_with_retry(url)
    except RequestException:
        return result

    soup = BeautifulSoup(response.text, "lxml")
    location_node = soup.select_one(settings.detail_location_selector)
    description_node = soup.select_one(settings.detail_description_selector)

    if location_node is not None:
        result["location"] = location_node.get_text(strip=True) or "Unknown"
    if description_node is not None:
        result["description"] = description_node.get_text(strip=True)

    return result

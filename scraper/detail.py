from bs4 import BeautifulSoup
from playwright.sync_api import Page

from scraper.config import settings
from scraper.utils import normalize_text

RATING_MAP = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}


def fetch_detail_with_status(item: dict[str, object], page: Page) -> tuple[dict[str, object], bool]:
    result = {**item, "category": "Unknown", "rating": "N/A", "availability": "Unknown", "description": ""}
    url = normalize_text(str(item.get("url", "")))
    if not url:
        return result, False

    try:
        page.goto(url, timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=5000)
        html = page.content()
    except Exception:
        return result, False

    soup = BeautifulSoup(html, "lxml")

    category = soup.select_one(settings.detail_category_selector)
    rating = soup.select_one(settings.detail_rating_selector)
    availability = soup.select_one(settings.detail_availability_selector)
    description = soup.select_one(settings.detail_description_selector)

    if category:
        result["category"] = normalize_text(category.get_text(strip=True)) or "Unknown"

    if rating:
        for cls in rating.get("class", []):
            if cls.lower() in RATING_MAP:
                result["rating"] = f"{RATING_MAP[cls.lower()]}/5"
                break

    if availability:
        result["availability"] = normalize_text(availability.get_text(strip=True)) or "Unknown"

    if description:
        result["description"] = normalize_text(description.get_text(strip=True))

    return result, True

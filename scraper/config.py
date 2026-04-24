"""Configuration for the scraper project."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    base_url: str = os.getenv("BASE_URL", "https://example.com")
    listing_path: str = os.getenv("LISTING_PATH", "/")
    item_selector: str = os.getenv("ITEM_SELECTOR", "article")
    title_selector: str = os.getenv("TITLE_SELECTOR", "h2")
    link_selector: str = os.getenv("LINK_SELECTOR", "a")
    price_selector: str = os.getenv("PRICE_SELECTOR", ".price")
    detail_location_selector: str = os.getenv("DETAIL_LOCATION_SELECTOR", ".location")
    detail_description_selector: str = os.getenv("DETAIL_DESCRIPTION_SELECTOR", ".description")
    max_pages: int = int(os.getenv("MAX_PAGES", "2"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    retry_min_wait_seconds: int = int(os.getenv("RETRY_MIN_WAIT_SECONDS", "1"))
    retry_max_wait_seconds: int = int(os.getenv("RETRY_MAX_WAIT_SECONDS", "5"))
    request_delay_min_seconds: float = float(os.getenv("REQUEST_DELAY_MIN_SECONDS", "0.6"))
    request_delay_max_seconds: float = float(os.getenv("REQUEST_DELAY_MAX_SECONDS", "1.8"))
    rotate_user_agent: bool = os.getenv("ROTATE_USER_AGENT", "true").lower() == "true"
    eur_to_inr_rate: float = float(os.getenv("EUR_TO_INR_RATE", "109.86"))
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    seen_urls_file: str = os.getenv("SEEN_URLS_FILE", "output/seen_urls.json")
    failed_detail_items_file: str = os.getenv(
        "FAILED_DETAIL_ITEMS_FILE",
        "output/failed_detail_items.json",
    )
    logs_dir: str = os.getenv("LOGS_DIR", "logs")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"


settings = Settings()

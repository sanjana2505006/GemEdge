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
    max_pages: int = int(os.getenv("MAX_PAGES", "2"))
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    logs_dir: str = os.getenv("LOGS_DIR", "logs")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"


settings = Settings()

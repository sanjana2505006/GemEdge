"""Configuration for the scraper project."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    base_url: str = os.getenv("BASE_URL", "https://example.com")
    output_dir: str = os.getenv("OUTPUT_DIR", "output")
    logs_dir: str = os.getenv("LOGS_DIR", "logs")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"


settings = Settings()

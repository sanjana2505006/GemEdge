"""Pipeline orchestration for assignment scaffold."""

from pathlib import Path
import csv

from loguru import logger

from scraper.browser import browser_session
from scraper.config import settings
from scraper.detail import fetch_detail
from scraper.listing import fetch_listing_items
from scraper.utils import ensure_dirs, write_json


def _write_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline() -> None:
    """Run a minimal end-to-end scrape flow with placeholder data."""
    ensure_dirs([settings.output_dir, settings.logs_dir])
    log_path = Path(settings.logs_dir) / "app.log"
    logger.add(log_path, rotation="500 KB")

    logger.info("Starting GemEdge scaffold pipeline")
    with browser_session(headless=settings.headless):
        listing_items = fetch_listing_items()
        detailed_items = [fetch_detail(item) for item in listing_items]

    json_path = Path(settings.output_dir) / "items.json"
    csv_path = Path(settings.output_dir) / "items.csv"
    write_json(str(json_path), detailed_items)
    _write_csv(str(csv_path), detailed_items)
    logger.info("Wrote {} records", len(detailed_items))

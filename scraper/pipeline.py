"""Pipeline orchestration for assignment scaffold."""

from pathlib import Path
import csv

from loguru import logger

from scraper.browser import browser_session
from scraper.config import settings
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
    """Run listing scrape and write JSON/CSV outputs."""
    ensure_dirs([settings.output_dir, settings.logs_dir])
    log_path = Path(settings.logs_dir) / "app.log"
    logger.add(log_path, rotation="500 KB")

    logger.info("Starting GemEdge scaffold pipeline")
    with browser_session(headless=settings.headless):
        listing_items = fetch_listing_items()

    json_path = Path(settings.output_dir) / "items.json"
    csv_path = Path(settings.output_dir) / "items.csv"
    write_json(str(json_path), listing_items)
    _write_csv(str(csv_path), listing_items)
    logger.info("Wrote {} listing records", len(listing_items))

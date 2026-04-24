"""Pipeline orchestration for assignment scaffold."""

from pathlib import Path
import csv

from loguru import logger

from scraper.browser import browser_session
from scraper.config import settings
from scraper.detail import fetch_detail
from scraper.listing import fetch_listing_items
from scraper.utils import ensure_dirs, read_json, write_json


def _write_csv(path: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline() -> None:
    """Run listing scrape + light detail enrichment."""
    ensure_dirs([settings.output_dir, settings.logs_dir])
    log_path = Path(settings.logs_dir) / "app.log"
    logger.add(log_path, rotation="500 KB")
    seen_urls_path = Path(settings.seen_urls_file)
    ensure_dirs([str(seen_urls_path.parent)])

    raw_seen = read_json(str(seen_urls_path), default=[])
    seen_urls = {str(url) for url in raw_seen if isinstance(url, str)}

    logger.info("Starting GemEdge scaffold pipeline")
    with browser_session(headless=settings.headless):
        listing_items = fetch_listing_items()
        new_items = [
            item
            for item in listing_items
            if isinstance(item.get("url"), str) and item["url"] not in seen_urls
        ]
        enriched_items = [fetch_detail(item) for item in new_items]

    json_path = Path(settings.output_dir) / "items.json"
    csv_path = Path(settings.output_dir) / "items.csv"
    write_json(str(json_path), enriched_items)
    _write_csv(str(csv_path), enriched_items)
    seen_urls.update(
        str(item["url"])
        for item in listing_items
        if isinstance(item.get("url"), str) and item["url"]
    )
    write_json(str(seen_urls_path), sorted(seen_urls))
    logger.info("Filtered {} already-seen items", len(listing_items) - len(new_items))
    logger.info("Wrote {} enriched records", len(enriched_items))

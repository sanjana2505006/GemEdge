import csv
import time
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from scraper.browser import browser_session
from scraper.config import settings
from scraper.detail import fetch_detail_with_status
from scraper.listing import fetch_listing_items
from scraper.utils import ensure_dirs, read_json, write_json


CSV_FIELDS = [
    "id", "title", "seller", "url", "price", "price_inr",
    "category", "rating", "availability", "scraped_date", "description",
]


def _write_csv(path: str, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else CSV_FIELDS
    with open(path, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def run_pipeline() -> None:
    ensure_dirs([settings.output_dir, settings.logs_dir])
    logger.add(Path(settings.logs_dir) / "app.log", rotation="500 KB")

    seen_urls_path = Path(settings.seen_urls_file)
    failed_path = Path(settings.failed_detail_items_file)
    ensure_dirs([str(seen_urls_path.parent)])

    seen_urls = set(read_json(str(seen_urls_path), default=[]))
    previous_failed = [
        i for i in read_json(str(failed_path), default=[])
        if isinstance(i, dict) and isinstance(i.get("url"), str)
    ]

    logger.info("Pipeline started")

    with browser_session(headless=settings.headless) as page:
        listing_items = fetch_listing_items(page)
        new_items = [i for i in listing_items if i.get("url") not in seen_urls]

        pending = {str(i["url"]): i for i in previous_failed}
        pending.update({str(i["url"]): i for i in new_items})
        pending_items = list(pending.values())

        detail_results = []
        success_count = 0

        for item in tqdm(pending_items, desc="Fetching details", unit="page"):
            time.sleep(0.5)
            result, ok = fetch_detail_with_status(item, page)
            detail_results.append((result, ok))
            if ok:
                success_count += 1

    successful = [i for i, ok in detail_results if ok]
    failed = [i for i, ok in detail_results if not ok]

    write_json(str(Path(settings.output_dir) / "items.json"), successful)
    _write_csv(str(Path(settings.output_dir) / "items.csv"), successful)

    summary = {
        "scraped_count": len(listing_items),
        "new_count": len(new_items),
        "already_seen_count": len(listing_items) - len(new_items),
        "detail_success_count": len(successful),
        "detail_failed_count": len(failed),
        "written_count": len(successful),
    }
    write_json(str(Path(settings.output_dir) / "run_summary.json"), summary)

    seen_urls.update(str(i["url"]) for i in successful if i.get("url"))
    write_json(str(seen_urls_path), sorted(seen_urls))
    write_json(str(failed_path), failed)

    logger.info("Done — {} records written, {} failed", len(successful), len(failed))

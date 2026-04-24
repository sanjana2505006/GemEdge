"""Pipeline orchestration for assignment scaffold."""

from pathlib import Path
import csv

from loguru import logger

from scraper.browser import browser_session
from scraper.config import settings
from scraper.detail import fetch_detail_with_status
from scraper.listing import fetch_listing_items
from scraper.utils import ensure_dirs, read_json, write_json
import time
from tqdm import tqdm


DEFAULT_CSV_FIELDS = [
    "id",
    "title",
    "seller",
    "url",
    "price",
    "price_inr",
    "category",
    "rating",
    "availability",
    "scraped_date",
    "description",
]


def _write_csv(path: str, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else DEFAULT_CSV_FIELDS
    with open(path, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def run_pipeline() -> None:
    """Run listing scrape + light detail enrichment."""
    ensure_dirs([settings.output_dir, settings.logs_dir])
    log_path = Path(settings.logs_dir) / "app.log"
    logger.add(log_path, rotation="500 KB")
    seen_urls_path = Path(settings.seen_urls_file)
    failed_items_path = Path(settings.failed_detail_items_file)
    ensure_dirs([str(seen_urls_path.parent), str(failed_items_path.parent)])

    raw_seen = read_json(str(seen_urls_path), default=[])
    seen_urls = {str(url) for url in raw_seen if isinstance(url, str)}
    raw_failed_items = read_json(str(failed_items_path), default=[])
    previous_failed_items = [
        item
        for item in raw_failed_items
        if isinstance(item, dict) and isinstance(item.get("url"), str) and item["url"]
    ]

    logger.info("Starting GemEdge scaffold pipeline")
    with browser_session(headless=settings.headless) as page:
        listing_items = fetch_listing_items(page)
        new_items = [
            item
            for item in listing_items
            if isinstance(item.get("url"), str) and item["url"] not in seen_urls
        ]

        pending_by_url = {
            str(item["url"]): item for item in previous_failed_items
        }
        for item in new_items:
            pending_by_url[str(item["url"])] = item
        pending_items = list(pending_by_url.values())

        # Progress bar for detail page extraction
        detail_progress = tqdm(
            pending_items,
            desc="🔍 Extracting details",
            unit="page",
            dynamic_ncols=True
        )
        
        detail_results = []
        success_count = 0
        for item in detail_progress:
            # Add delay to avoid overwhelming the server
            time.sleep(0.5)
            result, success = fetch_detail_with_status(item, page)
            detail_results.append((result, success))
            
            if success:
                success_count += 1
            
            # Update progress with success rate
            success_rate = (success_count / len(detail_results)) * 100
            detail_progress.set_postfix_str(f"Success: {success_count}/{len(detail_results)} ({success_rate:.1f}%)")
        
        detail_progress.close()
        
        successful_items = [item for item, ok in detail_results if ok]
        failed_items = [item for item, ok in detail_results if not ok]
        detail_success_count = len(successful_items)
        detail_failed_count = len(failed_items)

    # Final summary progress bar
    summary_progress = tqdm(
        total=4,
        desc="📊 Finalizing",
        unit="step",
        dynamic_ncols=True
    )
    
    summary_progress.set_description("💾 Saving JSON")
    json_path = Path(settings.output_dir) / "items.json"
    write_json(str(json_path), successful_items)
    summary_progress.update(1)
    
    summary_progress.set_description("📋 Saving CSV")
    csv_path = Path(settings.output_dir) / "items.csv"
    _write_csv(str(csv_path), successful_items)
    summary_progress.update(1)
    
    summary_progress.set_description("📈 Generating summary")
    summary = {
        "scraped_count": len(listing_items),
        "new_count": len(new_items),
        "retry_queue_in_count": len(previous_failed_items),
        "processed_detail_count": len(pending_items),
        "already_seen_count": len(listing_items) - len(new_items),
        "detail_success_count": detail_success_count,
        "detail_failed_count": detail_failed_count,
        "retry_queue_out_count": len(failed_items),
        "written_count": len(successful_items),
    }
    run_summary_path = Path(settings.output_dir) / "run_summary.json"
    write_json(str(run_summary_path), summary)
    summary_progress.update(1)
    
    summary_progress.set_description("🔚 Updating state")
    seen_urls.update(
        str(item["url"]) for item in successful_items if isinstance(item.get("url"), str) and item["url"]
    )
    write_json(str(seen_urls_path), sorted(seen_urls))
    write_json(str(failed_items_path), failed_items)
    summary_progress.update(1)
    
    summary_progress.set_postfix_str(f"✅ {summary['written_count']} items saved")
    summary_progress.close()
    
    logger.info("Filtered {} already-seen items", summary["already_seen_count"])
    logger.info(
        "Retry queue in={}, out={}",
        summary["retry_queue_in_count"],
        summary["retry_queue_out_count"],
    )
    logger.info(
        "Detail fetch success={}, failed={}",
        summary["detail_success_count"],
        summary["detail_failed_count"],
    )
    logger.info("Wrote {} enriched records", summary["written_count"])

# GemEdge Assignment

This repo has the initial project setup (roughly 10-20% done).

Current status:
- Basic scraper structure is in place
- Pipeline runs end-to-end
- Sample data is written to JSON and CSV
- Logging is enabled

Run locally:
1. `pip install -r requirements.txt`
2. Set `.env` values (example below)
3. `python main.py`

Suggested `.env` for this milestone:
- `BASE_URL=https://targetsite.com`
- `LISTING_PATH=/listings`
- `ITEM_SELECTOR=.listing-card`
- `TITLE_SELECTOR=.listing-title`
- `LINK_SELECTOR=a`
- `PRICE_SELECTOR=.listing-price`
- `MAX_PAGES=2`

The scraper currently focuses only on listing data:
- `id`
- `title`
- `url`
- `price`
- plus small detail enrichment:
  - `location`
  - `description`

Generated files:
- `output/items.json`
- `output/items.csv`
- `logs/app.log`

What is still pending:
- Real listing/detail scraping logic
- Pagination + deduplication
- Better error handling/retries
- Tests and validation checks

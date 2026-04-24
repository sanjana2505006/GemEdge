# GemEdge Assignment (Starter)

This is a **minimal 10-20% scaffold** for a scraping assignment.

## Current structure

- `main.py`: Entry point
- `scraper/config.py`: Environment-based settings
- `scraper/browser.py`: Browser session placeholder
- `scraper/listing.py`: Listing extraction stub
- `scraper/detail.py`: Detail extraction stub
- `scraper/pipeline.py`: End-to-end orchestration + JSON/CSV output
- `scraper/utils.py`: Utility helpers

## Quick start

1. Install dependencies in your virtual env:
   - `pip install -r requirements.txt`
2. Run:
   - `python main.py`

Outputs:
- `output/items.json`
- `output/items.csv`
- `logs/app.log`

## Next (remaining 80-90%)

- Replace placeholder extractors with real site selectors/API calls
- Add retry/timeouts and robust error handling
- Add pagination and deduplication
- Add unit tests and data validation

# GemEdge Assignment

This repo has the initial project setup (roughly 10-20% done).

Current status:
- Basic scraper structure is in place
- Pipeline runs end-to-end
- Sample data is written to JSON and CSV
- Logging is enabled

Run locally:
1. `pip install -r requirements.txt`
2. `python main.py`

Generated files:
- `output/items.json`
- `output/items.csv`
- `logs/app.log`

What is still pending:
- Real listing/detail scraping logic
- Pagination + deduplication
- Better error handling/retries
- Tests and validation checks

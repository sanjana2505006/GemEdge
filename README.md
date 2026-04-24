# GemEdge Data Scraping Assignment

A Python scraper that extracts structured book data from [books.toscrape.com](https://books.toscrape.com) — a JS-rendered listings site — and outputs clean CSV and JSON with prices converted to INR.

---

## Approach & Tools

- **Playwright** — headless Chromium to handle JavaScript-rendered pages
- **BeautifulSoup + lxml** — HTML parsing after JS execution
- **tenacity** — retry logic with exponential backoff on failures
- **loguru** — structured logging to file and console
- **python-dotenv** — all selectors and settings are config-driven via `.env`
- **tqdm** — progress bars for pagination and detail extraction

The pipeline runs in two stages:
1. **Listing scrape** — paginates through listing pages, extracts title, URL, and price (converted to INR)
2. **Detail enrichment** — visits each book's detail page to extract category, rating, availability, and description

---

## Data Extracted

| Field | Source |
|---|---|
| `id` | Derived from URL slug |
| `title` | Listing page |
| `url` | Listing page |
| `price` | Listing page (converted to INR) |
| `price_inr` | Listing page (numeric INR value) |
| `category` | Detail page (breadcrumb) |
| `rating` | Detail page (star rating class) |
| `availability` | Detail page |
| `description` | Detail page |

---

## Setup & Run

### Prerequisites
- Python 3.10 or higher — [python.org/downloads](https://www.python.org/downloads/)
- Git — [git-scm.com](https://git-scm.com/)

---

### macOS

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd GemEdge

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Run the scraper
python main.py

# 6. (Optional) Launch the dashboard
python app.py
# Then open http://127.0.0.1:5001 in your browser
```

---

### Windows

```cmd
# 1. Clone the repo
git clone <your-repo-url>
cd GemEdge

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Run the scraper
python main.py

# 6. (Optional) Launch the dashboard
python app.py
# Then open http://127.0.0.1:5001 in your browser
```

---

### Output

Output files are written to `output/`:
- `items.csv` — structured data in CSV format
- `items.json` — same data in JSON format
- `run_summary.json` — scrape stats (counts, success/fail rates)

Logs are written to `logs/app.log`.

---

## Challenges & How They Were Handled

- **Relative URLs** — books.toscrape.com uses `../../catalogue/...` style hrefs; handled by detecting and normalising relative paths before storing
- **Missing data** — all fields default gracefully (`"Unknown"`, `"N/A"`) so no row is dropped due to a missing field
- **Rate limiting** — random delay (0.6–1.8s) between requests plus rotating user-agent headers
- **Failed detail pages** — stored in `output/failed_detail_items.json` and retried on the next run
- **Deduplication** — `output/seen_urls.json` tracks all scraped URLs across runs

---

## What Would Break / How to Improve

- **Selector changes** — if the site updates its HTML structure, CSS selectors in `.env` need updating; a selector health-check on startup would help
- **Scale** — detail pages are fetched sequentially; async Playwright or a worker pool would speed this up significantly
- **Currency rate** — `EUR_TO_INR_RATE` is a static config value; integrating a live FX API (e.g. exchangerate.host) would keep it accurate
- **Anti-bot** — the current approach (delays + UA rotation) is basic; residential proxies or stealth plugins would be needed for stricter sites

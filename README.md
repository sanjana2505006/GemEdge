# GemEdge Book Scraper

A Python scraper that pulls structured book data from [books.toscrape.com](https://books.toscrape.com) and saves it as CSV and JSON with prices in INR.

---

## Tools Used

- **Playwright** — headless Chromium for JS-rendered pages
- **BeautifulSoup + lxml** — HTML parsing
- **tenacity** — retry logic with exponential backoff
- **loguru** — logging to file and console
- **python-dotenv** — config via `.env` file
- **tqdm** — progress bars during scraping

Scraping runs in two stages:
1. **Listing pages** — grabs title, URL, and price (converted to INR)
2. **Detail pages** — grabs category, rating, availability, and description

---

## Data Fields

| Field | Where it comes from |
|---|---|
| `id` | URL slug |
| `title` | Listing page |
| `url` | Listing page |
| `price` | Listing page (INR) |
| `price_inr` | Listing page (numeric) |
| `category` | Detail page |
| `rating` | Detail page |
| `availability` | Detail page |
| `description` | Detail page |

---

## Running on macOS

```bash
git clone <your-repo-url>
cd GemEdge

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

python main.py
```

To view the dashboard:

```bash
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## Running on Windows

```cmd
git clone <your-repo-url>
cd GemEdge

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium

python main.py
```

To view the dashboard:

```cmd
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## Output

- `output/items.csv` — scraped data in CSV
- `output/items.json` — scraped data in JSON
- `output/run_summary.json` — run stats
- `logs/app.log` — full logs

---

## Challenges

- **Relative URLs** — the site uses `../../catalogue/...` paths, normalised to absolute URLs before saving
- **Missing fields** — all fields fall back to `"Unknown"` or `"N/A"` so no rows are dropped
- **Rate limiting** — random 0.6–1.8s delay between requests with rotating user-agent headers
- **Failed pages** — saved to `output/failed_detail_items.json` and retried on the next run
- **Duplicate URLs** — tracked in `output/seen_urls.json` across runs

---

## What Could Be Better

- Selectors are config-driven but still need manual updates if the site changes its HTML
- Detail pages are fetched one at a time — a worker pool would speed things up a lot
- The INR conversion rate is static — hooking into a live FX API would keep it accurate

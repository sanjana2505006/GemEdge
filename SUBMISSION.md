# GemEdge Scraping — Write-up

**Name:** Sanjana
**Email:** gopal@gemedge.dev
**Deadline:** 25/04/2026 9:00 PM

---

## Approach & Tools

I built a Python scraper targeting books.toscrape.com, a JS-rendered listings site. I used **Playwright** (headless Chromium) to handle dynamic content, **BeautifulSoup + lxml** for HTML parsing, and **tenacity** for retry logic with exponential backoff. All configuration — selectors, pagination, delays, currency rate — lives in a `.env` file, keeping the code clean and reusable.

The pipeline runs in two stages: listing pages extract title, URL, and price; detail pages enrich each record with category, rating, availability, and description. Prices are converted from GBP to INR using a configurable exchange rate.

## Challenges

The biggest challenge was URL normalisation — the site uses relative paths like `../../catalogue/book-name/index.html` which needed custom handling to build correct absolute URLs. I also had to map word-based star ratings (e.g. "Three") to numeric values by parsing CSS class names.

## How I Handled Failures

Failed detail page fetches are saved to `output/failed_detail_items.json` and automatically retried on the next run. All fields fall back gracefully to `"Unknown"` or `"N/A"` so no records are dropped. Random delays (0.6–1.8s) and rotating user-agent headers reduce the chance of being blocked.

## What Would Break

If the site updates its HTML structure, the CSS selectors in `.env` would need updating. The INR conversion rate is also static — a live FX API would keep it accurate.

## How I'd Improve It

Fetch detail pages concurrently using async Playwright to cut runtime significantly. Add a selector health-check on startup to catch broken selectors early.

---

**Output files:** `output/items.csv`, `output/items.json`
**GitHub:** https://github.com/sanjana2505006/GemEdge

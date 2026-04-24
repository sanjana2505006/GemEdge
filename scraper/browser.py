from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import sync_playwright, Page
from loguru import logger


@contextmanager
def browser_session(headless: bool = True) -> Iterator[Page]:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    logger.info("Browser started")
    try:
        yield page
    finally:
        context.close()
        browser.close()
        playwright.stop()
        logger.info("Browser closed")

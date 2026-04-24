"""Browser automation using Playwright."""

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from loguru import logger


@contextmanager
def browser_session(headless: bool = True) -> Iterator[Page]:
    """
    Real Playwright browser context for JavaScript-heavy sites.
    
    Yields a Page object that can be used for scraping.
    """
    playwright = None
    browser = None
    context = None
    
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        logger.info("Browser session started")
        yield page
    except Exception as e:
        logger.error("Browser session error: {}", e)
        raise
    finally:
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        logger.info("Browser session closed")

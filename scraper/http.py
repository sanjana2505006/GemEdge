"""HTTP utilities with retry behavior."""

import random
import time

import requests
from requests import Response
from tenacity import retry, stop_after_attempt, wait_exponential

from scraper.config import settings

try:
    from fake_useragent import UserAgent
except Exception:  # pragma: no cover - fallback if provider fails
    UserAgent = None

_SESSION = requests.Session()
_FALLBACK_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_UA_PROVIDER = UserAgent() if (settings.rotate_user_agent and UserAgent is not None) else None


def _get_headers() -> dict[str, str]:
    user_agent = _FALLBACK_UA
    if _UA_PROVIDER is not None:
        try:
            user_agent = _UA_PROVIDER.random
        except Exception:
            user_agent = _FALLBACK_UA
    return {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }


def _polite_delay() -> None:
    min_wait = min(settings.request_delay_min_seconds, settings.request_delay_max_seconds)
    max_wait = max(settings.request_delay_min_seconds, settings.request_delay_max_seconds)
    time.sleep(random.uniform(min_wait, max_wait))


@retry(
    stop=stop_after_attempt(settings.retry_attempts),
    wait=wait_exponential(
        multiplier=1,
        min=settings.retry_min_wait_seconds,
        max=settings.retry_max_wait_seconds,
    ),
    reraise=True,
)
def _request_with_retry(url: str) -> Response:
    _polite_delay()
    response = _SESSION.get(
        url,
        timeout=settings.request_timeout_seconds,
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response


def get_with_retry(url: str) -> Response:
    """Issue GET with retries and bubble the original request error."""
    return _request_with_retry(url)

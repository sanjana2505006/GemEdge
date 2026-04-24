import random
import time

import requests
from requests import Response
from tenacity import retry, stop_after_attempt, wait_exponential

from scraper.config import settings

try:
    from fake_useragent import UserAgent
    _ua = UserAgent() if settings.rotate_user_agent else None
except Exception:
    _ua = None

_SESSION = requests.Session()
_FALLBACK_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _headers() -> dict[str, str]:
    ua = _FALLBACK_UA
    if _ua is not None:
        try:
            ua = _ua.random
        except Exception:
            pass
    return {
        "User-Agent": ua,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


@retry(
    stop=stop_after_attempt(settings.retry_attempts),
    wait=wait_exponential(min=settings.retry_min_wait_seconds, max=settings.retry_max_wait_seconds),
    reraise=True,
)
def get_with_retry(url: str) -> Response:
    time.sleep(random.uniform(settings.request_delay_min_seconds, settings.request_delay_max_seconds))
    response = _SESSION.get(url, timeout=settings.request_timeout_seconds, headers=_headers())
    response.raise_for_status()
    return response

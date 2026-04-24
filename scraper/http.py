"""HTTP utilities with retry behavior."""

import requests
from requests import Response
from tenacity import retry, stop_after_attempt, wait_exponential

from scraper.config import settings


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
    response = requests.get(url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return response


def get_with_retry(url: str) -> Response:
    """Issue GET with retries and bubble the original request error."""
    return _request_with_retry(url)

"""Browser helpers (placeholder for Playwright integration)."""

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def browser_session(headless: bool = True) -> Iterator[None]:
    """
    Minimal browser context placeholder.

    Replace this with real Playwright setup in the next iteration.
    """
    _ = headless
    yield None

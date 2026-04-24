"""Utility helpers shared across scraper modules."""

from pathlib import Path
from typing import Iterable
import json
import re
from urllib.parse import urldefrag, urljoin


def ensure_dirs(paths: Iterable[str]) -> None:
    """Create directories if they do not exist."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def write_json(path: str, payload: object) -> None:
    """Write structured data to JSON file."""
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def normalize_text(value: str) -> str:
    """Trim and collapse repeated whitespace."""
    return " ".join(value.split()).strip()


def normalize_url(base_url: str, href: str) -> str:
    """Build absolute URL and remove fragment part."""
    absolute = urljoin(base_url, href.strip())
    clean, _fragment = urldefrag(absolute)
    return clean


def parse_price_value(price_text: str) -> float | None:
    """Extract numeric value from common price formats."""
    normalized = normalize_text(price_text)
    if not normalized:
        return None

    match = re.search(r"\d[\d,]*(?:\.\d+)?", normalized)
    if not match:
        return None
    raw = match.group(0).replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None

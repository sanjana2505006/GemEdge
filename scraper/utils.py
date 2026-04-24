"""Utility helpers shared across scraper modules."""

from pathlib import Path
from typing import Iterable
import json


def ensure_dirs(paths: Iterable[str]) -> None:
    """Create directories if they do not exist."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def write_json(path: str, payload: object) -> None:
    """Write structured data to JSON file."""
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)

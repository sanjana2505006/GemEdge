import json
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urldefrag, urljoin


def ensure_dirs(paths: Iterable[str]) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def write_json(path: str, payload: object) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def read_json(path: str, default: object) -> object:
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except (json.JSONDecodeError, OSError):
        return default


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()


def normalize_url(base_url: str, href: str) -> str:
    absolute = urljoin(base_url, href.strip())
    clean, _ = urldefrag(absolute)
    return clean


def parse_price_value(price_text: str) -> float | None:
    normalized = normalize_text(price_text)
    if not normalized:
        return None
    match = re.search(r"\d[\d,]*(?:\.\d+)?", normalized)
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None

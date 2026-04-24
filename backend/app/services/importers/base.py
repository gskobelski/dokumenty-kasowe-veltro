from __future__ import annotations

from collections.abc import Iterable
import unicodedata


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return stripped.translate(
        str.maketrans(
            {
                "ł": "l",
                "Ł": "L",
            }
        )
    )


def normalize_key(value: str) -> str:
    stripped = _strip_accents(value)
    return "".join(ch.lower() for ch in stripped if ch.isalnum())


def find_value(row: dict[str, object], candidates: Iterable[str]) -> str:
    normalized_map = {normalize_key(str(key)): value for key, value in row.items()}
    for candidate in candidates:
        value = normalized_map.get(normalize_key(candidate))
        if value is None:
            continue
        return str(value).strip()
    return ""


def normalize_text(value: str) -> str:
    stripped = _strip_accents(value)
    return " ".join(stripped.lower().split())

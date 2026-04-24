from __future__ import annotations

from collections.abc import Iterable


def normalize_key(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def find_value(row: dict[str, object], candidates: Iterable[str]) -> str:
    normalized_map = {normalize_key(str(key)): value for key, value in row.items()}
    for candidate in candidates:
        value = normalized_map.get(normalize_key(candidate))
        if value is None:
            continue
        return str(value).strip()
    return ""


def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


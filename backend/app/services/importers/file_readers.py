from __future__ import annotations

import csv
from io import BytesIO, StringIO

from openpyxl import load_workbook


def read_tabular_bytes(filename: str, payload: bytes) -> list[dict[str, object]]:
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix == "csv":
        return _read_csv(payload)
    if suffix in {"xlsx", "xlsm"}:
        return _read_xlsx(payload)
    raise ValueError(f"Unsupported file format: {filename}")


def _read_csv(payload: bytes) -> list[dict[str, object]]:
    text = payload.decode("utf-8-sig", errors="ignore")
    sample = text[:2048]
    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    reader = csv.DictReader(StringIO(text), delimiter=delimiter)
    return [dict(row) for row in reader]


def _read_xlsx(payload: bytes) -> list[dict[str, object]]:
    workbook = load_workbook(BytesIO(payload), read_only=True, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    result: list[dict[str, object]] = []
    for row in rows[1:]:
        result.append({headers[index]: value for index, value in enumerate(row)})
    return result


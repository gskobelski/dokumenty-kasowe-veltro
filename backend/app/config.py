from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    app_name: str = "Cash Documents API"
    edi_version: str = "1.05.1"
    communication_goal: int = 0
    code_page: int = 1250
    database_path: Path = Path("cash_documents.db")
    program_name: str = "dokumenty-kasowe-veltro"


def get_settings() -> Settings:
    db_path = Path(os.environ.get("DATABASE_PATH", "cash_documents.db"))
    return Settings(database_path=db_path)


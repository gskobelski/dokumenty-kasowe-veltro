from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.db import Database
from app.schemas import AppSettings

router = APIRouter(tags=["settings"])


@router.get("", response_model=AppSettings)
def get_settings(db: Database = Depends(get_db)) -> AppSettings:
    return db.get_settings()


@router.put("", response_model=AppSettings)
def save_settings(payload: AppSettings, db: Database = Depends(get_db)) -> AppSettings:
    return db.save_settings(payload)


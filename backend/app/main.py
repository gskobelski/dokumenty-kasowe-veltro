from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.documents import router as documents_router
from app.api.routes.export import router as export_router
from app.api.routes.imports import router as imports_router
from app.api.routes.settings import router as settings_router
from app.config import get_settings
from app.db import Database


def create_app(database_path: str | None = None) -> FastAPI:
    settings = get_settings()
    db_path = Path(database_path) if database_path else settings.database_path
    db = Database(db_path)

    app = FastAPI(title=settings.app_name)
    app.state.db = db
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(imports_router, prefix="/api/imports")
    app.include_router(documents_router, prefix="/api/documents")
    app.include_router(settings_router, prefix="/api/settings")
    app.include_router(export_router, prefix="/api/export")
    return app


app = create_app()


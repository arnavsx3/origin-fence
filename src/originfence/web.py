"""Local FastAPI dashboard application."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from originfence.store import EventStore


def create_app(database_path: Path = Path("data/originfence.sqlite3")) -> FastAPI:
    """Create a local-only dashboard for recent OriginFence sessions."""
    app = FastAPI(title="OriginFence", version="0.1.0")
    store = EventStore(database_path)
    dashboard = Path(__file__).resolve().parent / "templates" / "index.html"

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(dashboard)

    @app.get("/api/timeline")
    def timeline(session_id: str | None = None) -> list[dict[str, object]]:
        return store.timeline(session_id)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "storage": "local"}

    return app


app = create_app()

from pathlib import Path

from fastapi.testclient import TestClient

from originfence.web import create_app


def test_health_endpoint_reports_local_storage(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path / "events.sqlite3"))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "storage": "local"}

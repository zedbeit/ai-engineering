from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from intake_service.main import app


@pytest.fixture
def db_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    monkeypatch.setenv("INTAKE_DB_PATH", str(path))
    return path


@pytest.fixture
def client(db_path: Path) -> TestClient:
    return TestClient(app)

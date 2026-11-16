from pathlib import Path

from fastapi.testclient import TestClient

from intake_service.main import app


def test_documents_survive_a_restart(db_path: Path) -> None:
    first_client = TestClient(app)
    created = first_client.post(
        "/documents", json={"title": "Receipt 14", "text": "Rent"}
    )
    assert created.status_code == 201
    document_id = created.json()["id"]

    second_client = TestClient(app)
    response = second_client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Receipt 14"
    assert db_path.exists()

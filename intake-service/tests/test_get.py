from fastapi.testclient import TestClient


def test_get_returns_404_for_a_missing_id(client: TestClient) -> None:
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_get_returns_the_full_document(client: TestClient) -> None:
    created = client.post(
        "/documents",
        json={"title": "Receipt 14", "text": "Rent for November: 250,000"},
    )
    assert created.status_code == 201
    document = created.json()

    response = client.get(f"/documents/{document['id']}")

    assert response.status_code == 200
    assert response.json() == document
    assert response.json()["text"] == "Rent for November: 250,000"


def test_get_returns_422_for_a_non_integer_id(client: TestClient) -> None:
    response = client.get("/documents/abc")

    assert response.status_code == 422

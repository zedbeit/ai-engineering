import pytest
from fastapi.testclient import TestClient


def create(client: TestClient, title: str, text: str) -> int:
    response = client.post("/documents", json={"title": title, "text": text})
    assert response.status_code == 201
    document_id: int = response.json()["id"]
    return document_id


def test_delete_returns_204_with_an_empty_body(client: TestClient) -> None:
    created = client.post("/documents", json={"title": "Receipt 14", "text": "Rent"})
    assert created.status_code == 201
    document_id = created.json()["id"]

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_deleted_document_cannot_be_fetched(client: TestClient) -> None:
    document_id = create(client, "Receipt 14", "Rent")
    assert client.delete(f"/documents/{document_id}").status_code == 204

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_deleted_document_is_not_in_the_list(client: TestClient) -> None:
    deleted_id = create(client, "Receipt 14", "Rent")
    kept_id = create(client, "Receipt 15", "Fuel")
    assert client.delete(f"/documents/{deleted_id}").status_code == 204

    response = client.get("/documents")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [kept_id]


def test_delete_twice_returns_404(client: TestClient) -> None:
    document_id = create(client, "Receipt 14", "Rent")
    assert client.delete(f"/documents/{document_id}").status_code == 204

    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_delete_returns_404_for_a_missing_id(client: TestClient) -> None:
    response = client.delete("/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_delete_returns_422_for_a_non_integer_id(client: TestClient) -> None:
    response = client.delete("/documents/abc")

    assert response.status_code == 422


def test_id_is_not_reused_after_a_delete(client: TestClient) -> None:
    create(client, "Receipt 14", "Rent")
    newest_id = create(client, "Receipt 15", "Fuel")
    assert client.delete(f"/documents/{newest_id}").status_code == 204

    next_id = create(client, "Receipt 16", "Data bundle")

    assert next_id > newest_id


@pytest.mark.parametrize(
    "document_id",
    [
        pytest.param("0", id="zero"),
        pytest.param("-1", id="negative"),
        pytest.param("9223372036854775808", id="just-above-sqlite-max"),
        pytest.param("99999999999999999999", id="far-above-sqlite-max"),
    ],
)
def test_delete_returns_404_for_ids_no_document_can_have(
    client: TestClient, document_id: str
) -> None:
    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

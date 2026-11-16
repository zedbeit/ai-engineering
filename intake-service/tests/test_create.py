import re
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient


def test_create_returns_201_and_the_full_document(client: TestClient) -> None:
    response = client.post(
        "/documents",
        json={"title": "Receipt 14", "text": "Rent for November: 250,000"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Receipt 14"
    assert body["text"] == "Rent for November: 250,000"
    assert set(body) == {"id", "title", "text", "created_at"}


def test_create_trims_the_title(client: TestClient) -> None:
    response = client.post(
        "/documents", json={"title": "  Receipt 14  ", "text": "Rent"}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Receipt 14"


def test_create_stores_the_text_untrimmed(client: TestClient) -> None:
    response = client.post(
        "/documents", json={"title": "Receipt 14", "text": "  Rent\n"}
    )

    assert response.status_code == 201
    assert response.json()["text"] == "  Rent\n"


def test_create_ignores_extra_fields(client: TestClient) -> None:
    response = client.post(
        "/documents",
        json={
            "title": "Receipt 15",
            "text": "Fuel",
            "author": "Dee",
            "id": 99,
            "created_at": "2000-01-01T00:00:00Z",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "title", "text", "created_at"}
    assert body["id"] == 1
    assert body["created_at"] != "2000-01-01T00:00:00Z"


def test_create_sets_created_at_in_utc_iso_format(client: TestClient) -> None:
    response = client.post("/documents", json={"title": "Receipt 14", "text": "Rent"})

    assert response.status_code == 201
    created_at = response.json()["created_at"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", created_at)
    parsed = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert abs(datetime.now(UTC) - parsed) < timedelta(minutes=1)


def test_create_accepts_a_200_character_title(client: TestClient) -> None:
    title = "a" * 200

    response = client.post("/documents", json={"title": f"  {title}  ", "text": "x"})

    assert response.status_code == 201
    assert response.json()["title"] == title


def test_create_accepts_a_100_000_character_text(client: TestClient) -> None:
    text = "a" * 100_000

    response = client.post("/documents", json={"title": "Big", "text": text})

    assert response.status_code == 201
    assert response.json()["text"] == text


def test_create_allows_duplicate_titles(client: TestClient) -> None:
    body = {"title": "Receipt 14", "text": "Rent"}

    first = client.post("/documents", json=body)
    second = client.post("/documents", json=body)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({"text": "Fuel"}, id="no-title"),
        pytest.param({"title": None, "text": "Fuel"}, id="null-title"),
        pytest.param({"title": 123, "text": "Fuel"}, id="title-not-a-string"),
        pytest.param({"title": "", "text": "Fuel"}, id="empty-title"),
        pytest.param({"title": "   ", "text": "Fuel"}, id="whitespace-title"),
        pytest.param({"title": "a" * 201, "text": "Fuel"}, id="title-too-long"),
        pytest.param({"title": "Receipt"}, id="no-text"),
        pytest.param({"title": "Receipt", "text": None}, id="null-text"),
        pytest.param({"title": "Receipt", "text": 123}, id="text-not-a-string"),
        pytest.param({"title": "Receipt", "text": ""}, id="empty-text"),
        pytest.param({"title": "Receipt", "text": " \n "}, id="whitespace-text"),
        pytest.param({"title": "Receipt", "text": "a" * 100_001}, id="text-too-long"),
    ],
)
def test_create_rejects_invalid_input(client: TestClient, body: dict[str, Any]) -> None:
    response = client.post("/documents", json=body)

    assert response.status_code == 422


def test_create_rejects_a_body_that_is_not_an_object(client: TestClient) -> None:
    response = client.post("/documents", json=["Receipt", "Fuel"])

    assert response.status_code == 422


def test_create_stores_nothing_when_rejected(client: TestClient) -> None:
    rejected = client.post("/documents", json={"title": "   ", "text": "Fuel"})
    assert rejected.status_code == 422

    listed = client.get("/documents")

    assert listed.status_code == 200
    assert listed.json() == []

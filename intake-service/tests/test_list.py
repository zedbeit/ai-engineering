from fastapi.testclient import TestClient


def create(client: TestClient, title: str, text: str) -> int:
    response = client.post("/documents", json={"title": title, "text": text})
    assert response.status_code == 201
    document_id: int = response.json()["id"]
    return document_id


def search_ids(client: TestClient, term: str) -> list[int]:
    response = client.get("/documents", params={"search": term})
    assert response.status_code == 200
    return [item["id"] for item in response.json()]


def test_search_matches_the_text_ignoring_case(client: TestClient) -> None:
    rent_id = create(client, "Receipt 14", "Rent for November: 250,000")
    create(client, "Receipt 15", "Fuel")

    response = client.get("/documents", params={"search": "RENT"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [rent_id]


def test_list_returns_an_empty_list_when_there_are_no_documents(
    client: TestClient,
) -> None:
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_all_documents_ordered_by_id(client: TestClient) -> None:
    first = create(client, "Receipt 14", "Rent")
    second = create(client, "Receipt 15", "Fuel")
    third = create(client, "Receipt 16", "Data bundle")

    response = client.get("/documents")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [first, second, third]
    assert first < second < third


def test_list_items_are_summaries_without_text(client: TestClient) -> None:
    document_id = create(client, "Receipt 14", "Rent")

    response = client.get("/documents")

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert set(items[0]) == {"id", "title", "created_at"}
    assert items[0]["id"] == document_id
    assert items[0]["title"] == "Receipt 14"


def test_search_matches_the_title(client: TestClient) -> None:
    create(client, "Receipt 14", "Rent")
    fuel_id = create(client, "Receipt 15", "Fuel")

    assert search_ids(client, "receipt 15") == [fuel_id]


def test_search_matches_part_of_a_word(client: TestClient) -> None:
    account_id = create(client, "Statement", "Current account, November")
    create(client, "Receipt 15", "Fuel")

    assert search_ids(client, "rent") == [account_id]


def test_empty_search_returns_all_documents(client: TestClient) -> None:
    first = create(client, "Receipt 14", "Rent")
    second = create(client, "Receipt 15", "Fuel")

    assert search_ids(client, "") == [first, second]


def test_search_with_no_matches_returns_an_empty_list(client: TestClient) -> None:
    create(client, "Receipt 14", "Rent")

    assert search_ids(client, "salary") == []


def test_search_treats_percent_as_an_ordinary_character(client: TestClient) -> None:
    create(client, "Receipt 14", "Rent")
    discount_id = create(client, "Receipt 15", "Discount of 100% applied")

    assert search_ids(client, "%") == [discount_id]
    assert search_ids(client, "100%") == [discount_id]


def test_search_treats_underscore_as_an_ordinary_character(client: TestClient) -> None:
    create(client, "Export", "fileXname")
    underscore_id = create(client, "Export", "file_name")

    assert search_ids(client, "file_name") == [underscore_id]
    assert search_ids(client, "_") == [underscore_id]

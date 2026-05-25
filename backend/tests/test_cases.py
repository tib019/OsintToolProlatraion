import pytest
from httpx import AsyncClient


async def test_list_cases_empty(client: AsyncClient):
    response = await client.get("/api/cases/")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_case(client: AsyncClient):
    payload = {"name": "Test Case", "description": "A test case", "tags": ["osint"]}
    response = await client.post("/api/cases/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Case"
    assert data["description"] == "A test case"
    assert data["tags"] == ["osint"]
    assert "id" in data


async def test_get_case(client: AsyncClient):
    create = await client.post("/api/cases/", json={"name": "GetMe"})
    case_id = create.json()["id"]

    response = await client.get(f"/api/cases/{case_id}")
    assert response.status_code == 200
    assert response.json()["id"] == case_id


async def test_get_case_not_found(client: AsyncClient):
    response = await client.get("/api/cases/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_update_case(client: AsyncClient):
    create = await client.post("/api/cases/", json={"name": "Original"})
    case_id = create.json()["id"]

    response = await client.patch(f"/api/cases/{case_id}", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


async def test_delete_case(client: AsyncClient):
    create = await client.post("/api/cases/", json={"name": "ToDelete"})
    case_id = create.json()["id"]

    response = await client.delete(f"/api/cases/{case_id}")
    assert response.status_code == 204

    get = await client.get(f"/api/cases/{case_id}")
    assert get.status_code == 404


async def test_delete_case_not_found(client: AsyncClient):
    response = await client.delete("/api/cases/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

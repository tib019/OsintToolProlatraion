import pytest
from httpx import AsyncClient


@pytest.fixture
async def case_id(client: AsyncClient) -> str:
    r = await client.post("/api/cases/", json={"name": "Graph Test Case"})
    assert r.status_code == 201
    return r.json()["id"]


@pytest.fixture
async def node_id(client: AsyncClient, case_id: str) -> str:
    r = await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "IPAddress", "value": "1.2.3.4", "label": "1.2.3.4"},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def test_add_node(client: AsyncClient, case_id: str):
    r = await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "EmailAddress", "value": "test@example.com", "label": "test@example.com"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["entity_type"] == "EmailAddress"
    assert data["value"] == "test@example.com"
    assert "id" in data


async def test_add_node_case_not_found(client: AsyncClient):
    r = await client.post(
        "/api/graph/00000000-0000-0000-0000-000000000000/nodes",
        json={"entity_type": "Domain", "value": "example.com", "label": "example.com"},
    )
    assert r.status_code == 404


async def test_add_edge(client: AsyncClient, case_id: str):
    n1 = await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "Person", "value": "Alice", "label": "Alice"},
    )
    n2 = await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "EmailAddress", "value": "alice@example.com", "label": "alice@example.com"},
    )
    r = await client.post(
        f"/api/graph/{case_id}/edges",
        json={
            "source_id": n1.json()["id"],
            "target_id": n2.json()["id"],
            "label": "has_email",
            "transform_name": "manual",
        },
    )
    assert r.status_code == 201
    assert r.json()["label"] == "has_email"


async def test_add_edge_invalid_source(client: AsyncClient, case_id: str):
    n = await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "Domain", "value": "x.com", "label": "x.com"},
    )
    r = await client.post(
        f"/api/graph/{case_id}/edges",
        json={
            "source_id": "00000000-0000-0000-0000-000000000000",
            "target_id": n.json()["id"],
            "label": "link",
            "transform_name": "manual",
        },
    )
    assert r.status_code == 404


async def test_update_node_position(client: AsyncClient, case_id: str, node_id: str):
    r = await client.patch(
        f"/api/graph/{case_id}/nodes/{node_id}/position",
        json={"x": 100.0, "y": 200.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["pos_x"] == 100.0
    assert data["pos_y"] == 200.0


async def test_delete_node(client: AsyncClient, case_id: str, node_id: str):
    r = await client.delete(f"/api/graph/{case_id}/nodes/{node_id}")
    assert r.status_code == 204


async def test_delete_node_not_found(client: AsyncClient, case_id: str):
    r = await client.delete(
        f"/api/graph/{case_id}/nodes/00000000-0000-0000-0000-000000000000"
    )
    assert r.status_code == 404


async def test_graph_state_via_case(client: AsyncClient, case_id: str):
    await client.post(
        f"/api/graph/{case_id}/nodes",
        json={"entity_type": "Username", "value": "hunter2", "label": "hunter2"},
    )
    r = await client.get(f"/api/cases/{case_id}/graph")
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 1

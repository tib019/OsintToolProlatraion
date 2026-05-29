"""Integration tests for the Export API (JSON, CSV, PDF, SVG, PNG)."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def populated_case(client: AsyncClient):
    """Create a case with two nodes and an edge."""
    case = await client.post("/api/cases/", json={"name": "Export Test"})
    cid = case.json()["id"]

    n1 = await client.post(
        f"/api/graph/{cid}/nodes",
        json={"entity_type": "PhoneNumber", "value": "+4915123456789", "label": "+4915123456789"},
    )
    n2 = await client.post(
        f"/api/graph/{cid}/nodes",
        json={"entity_type": "Person", "value": "Max Mustermann", "label": "Max Mustermann"},
    )
    await client.post(
        f"/api/graph/{cid}/edges",
        json={
            "source_id": n1.json()["id"],
            "target_id": n2.json()["id"],
            "label": "caller_id",
            "transform_name": "CNAM / Reverse Lookup",
        },
    )
    return cid


# ---------------------------------------------------------------------------
# JSON Export
# ---------------------------------------------------------------------------

async def test_export_json_structure(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/json")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    data = r.json()
    assert "case" in data
    assert "nodes" in data
    assert "edges" in data
    assert data["case"]["id"] == populated_case
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1


async def test_export_json_node_fields(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/json")
    node = r.json()["nodes"][0]
    assert "id" in node
    assert "entity_type" in node
    assert "value" in node
    assert "label" in node
    assert "created_at" in node


async def test_export_json_edge_fields(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/json")
    edge = r.json()["edges"][0]
    assert "source_id" in edge
    assert "target_id" in edge
    assert "label" in edge
    assert "transform_name" in edge


async def test_export_json_case_not_found(client: AsyncClient):
    r = await client.get("/api/export/00000000-0000-0000-0000-000000000000/json")
    assert r.status_code == 404


async def test_export_json_empty_case(client: AsyncClient):
    case = await client.post("/api/cases/", json={"name": "Empty"})
    cid = case.json()["id"]
    r = await client.get(f"/api/export/{cid}/json")
    assert r.status_code == 200
    data = r.json()
    assert data["nodes"] == []
    assert data["edges"] == []


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

async def test_export_csv_returns_csv(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    text = r.text
    assert "=== NODES ===" in text
    assert "=== EDGES ===" in text


async def test_export_csv_contains_values(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/csv")
    text = r.text
    assert "+4915123456789" in text
    assert "Max Mustermann" in text
    assert "caller_id" in text


async def test_export_csv_case_not_found(client: AsyncClient):
    r = await client.get("/api/export/00000000-0000-0000-0000-000000000000/csv")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# SVG Export
# ---------------------------------------------------------------------------

async def test_export_svg_returns_svg(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/svg")
    assert r.status_code == 200
    assert "image/svg+xml" in r.headers["content-type"]
    assert r.text.startswith("<svg")
    assert "</svg>" in r.text


async def test_export_svg_contains_nodes(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/svg")
    assert "<circle" in r.text
    assert "Max Mustermann" in r.text


async def test_export_svg_case_not_found(client: AsyncClient):
    r = await client.get("/api/export/00000000-0000-0000-0000-000000000000/svg")
    assert r.status_code == 404


async def test_export_svg_empty_case(client: AsyncClient):
    case = await client.post("/api/cases/", json={"name": "Empty SVG"})
    r = await client.get(f"/api/export/{case.json()['id']}/svg")
    assert r.status_code == 200
    assert "<svg" in r.text


# ---------------------------------------------------------------------------
# PNG Export
# ---------------------------------------------------------------------------

async def test_export_png_returns_image(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    # PNG magic bytes
    assert r.content[:4] == b"\x89PNG"


async def test_export_png_case_not_found(client: AsyncClient):
    r = await client.get("/api/export/00000000-0000-0000-0000-000000000000/png")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Content-Disposition headers
# ---------------------------------------------------------------------------

async def test_export_json_has_download_header(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/json")
    assert "attachment" in r.headers.get("content-disposition", "")
    assert ".json" in r.headers.get("content-disposition", "")


async def test_export_csv_has_download_header(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/csv")
    assert "attachment" in r.headers.get("content-disposition", "")
    assert ".csv" in r.headers.get("content-disposition", "")


async def test_export_svg_has_download_header(client: AsyncClient, populated_case: str):
    r = await client.get(f"/api/export/{populated_case}/svg")
    assert "attachment" in r.headers.get("content-disposition", "")
    assert ".svg" in r.headers.get("content-disposition", "")

"""Integration tests for the Transforms API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def case_with_node(client: AsyncClient):
    """Case + one PhoneNumber node."""
    case = await client.post("/api/cases/", json={"name": "Transform API Test"})
    cid = case.json()["id"]
    node = await client.post(
        f"/api/graph/{cid}/nodes",
        json={"entity_type": "PhoneNumber", "value": "+4915123456789", "label": "+4915123456789"},
    )
    return cid, node.json()["id"]


# ---------------------------------------------------------------------------
# GET /api/transforms/ — list all transforms
# ---------------------------------------------------------------------------

async def test_list_transforms_returns_list(client: AsyncClient):
    r = await client.get("/api/transforms/")
    assert r.status_code == 200
    transforms = r.json()
    assert isinstance(transforms, list)
    assert len(transforms) == 10


async def test_list_transforms_fields(client: AsyncClient):
    r = await client.get("/api/transforms/")
    t = r.json()[0]
    assert "name" in t
    assert "description" in t
    assert "input_types" in t
    assert "output_types" in t
    assert "timeout" in t
    assert "rate_limit" in t


async def test_list_transforms_contains_phoneinfoga(client: AsyncClient):
    r = await client.get("/api/transforms/")
    names = [t["name"] for t in r.json()]
    assert "PhoneInfoga Scanner" in names
    assert "Leak Database Check" in names
    assert "IP/Domain Intelligence" in names


# ---------------------------------------------------------------------------
# GET /api/transforms/entity/{type} — transforms for entity type
# ---------------------------------------------------------------------------

async def test_transforms_for_phone_number(client: AsyncClient):
    r = await client.get("/api/transforms/entity/PhoneNumber")
    assert r.status_code == 200
    transforms = r.json()
    assert len(transforms) >= 5
    names = {t["name"] for t in transforms}
    assert "PhoneInfoga Scanner" in names
    assert "Platform Registration Checker" in names
    assert "CNAM / Reverse Lookup" in names
    assert "Leak Database Check" in names
    assert "Social Media Profile Linker" in names


async def test_transforms_for_email(client: AsyncClient):
    r = await client.get("/api/transforms/entity/EmailAddress")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()}
    assert "Leak Database Check" in names
    assert "Email OSINT" in names


async def test_transforms_for_ip(client: AsyncClient):
    r = await client.get("/api/transforms/entity/IPAddress")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()}
    assert "IP/Domain Intelligence" in names


async def test_transforms_for_unknown_type_returns_empty(client: AsyncClient):
    r = await client.get("/api/transforms/entity/Unicorn")
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# POST /api/transforms/run — queue a transform
# ---------------------------------------------------------------------------

async def test_run_transform_returns_job_id(client: AsyncClient, case_with_node):
    cid, nid = case_with_node
    r = await client.post(
        "/api/transforms/run",
        json={"case_id": cid, "node_id": nid, "transform_name": "PhoneInfoga Scanner"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    assert data["status"] == "queued"


async def test_run_transform_unknown_transform(client: AsyncClient, case_with_node):
    cid, nid = case_with_node
    r = await client.post(
        "/api/transforms/run",
        json={"case_id": cid, "node_id": nid, "transform_name": "Does Not Exist"},
    )
    assert r.status_code == 404


async def test_run_transform_case_not_found(client: AsyncClient, case_with_node):
    _, nid = case_with_node
    r = await client.post(
        "/api/transforms/run",
        json={
            "case_id": "00000000-0000-0000-0000-000000000000",
            "node_id": nid,
            "transform_name": "PhoneInfoga Scanner",
        },
    )
    assert r.status_code == 404


async def test_run_transform_node_not_found(client: AsyncClient, case_with_node):
    cid, _ = case_with_node
    r = await client.post(
        "/api/transforms/run",
        json={
            "case_id": cid,
            "node_id": "00000000-0000-0000-0000-000000000000",
            "transform_name": "PhoneInfoga Scanner",
        },
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/transforms/job/{job_id} — job status
# ---------------------------------------------------------------------------

async def test_get_job_status(client: AsyncClient, case_with_node):
    cid, nid = case_with_node
    run_r = await client.post(
        "/api/transforms/run",
        json={"case_id": cid, "node_id": nid, "transform_name": "PhoneInfoga Scanner"},
    )
    job_id = run_r.json()["job_id"]

    r = await client.get(f"/api/transforms/job/{job_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["job_id"] == job_id
    assert data["status"] in ("queued", "running", "completed", "error")


async def test_get_job_not_found(client: AsyncClient):
    r = await client.get("/api/transforms/job/nonexistent-job-id")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Audit log entry created after transform queued
# ---------------------------------------------------------------------------

async def test_transform_queued_creates_audit_log(client: AsyncClient, case_with_node):
    cid, nid = case_with_node
    await client.post(
        "/api/transforms/run",
        json={"case_id": cid, "node_id": nid, "transform_name": "PhoneInfoga Scanner"},
    )
    audit_r = await client.get(f"/api/cases/{cid}/audit")
    assert audit_r.status_code == 200
    events = [e["event_type"] for e in audit_r.json()]
    assert "transform_queued" in events

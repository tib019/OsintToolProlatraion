from httpx import AsyncClient


async def test_list_api_keys_empty(client: AsyncClient):
    r = await client.get("/api/settings/api-keys")
    assert r.status_code == 200
    assert r.json() == []


async def test_set_api_key(client: AsyncClient):
    r = await client.post(
        "/api/settings/api-keys",
        json={"service_name": "shodan", "key": "test-key-123"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["service_name"] == "shodan"
    assert data["is_set"] is True
    assert data["is_active"] is True


async def test_set_api_key_idempotent(client: AsyncClient):
    await client.post("/api/settings/api-keys", json={"service_name": "hibp", "key": "key-v1"})
    r = await client.post("/api/settings/api-keys", json={"service_name": "hibp", "key": "key-v2"})
    assert r.status_code == 201
    assert r.json()["is_set"] is True


async def test_list_api_keys_after_set(client: AsyncClient):
    await client.post("/api/settings/api-keys", json={"service_name": "shodan", "key": "abc"})
    r = await client.get("/api/settings/api-keys")
    assert r.status_code == 200
    names = [k["service_name"] for k in r.json()]
    assert "shodan" in names


async def test_activate_deactivate_api_key(client: AsyncClient):
    await client.post("/api/settings/api-keys", json={"service_name": "shodan", "key": "abc"})

    r = await client.patch("/api/settings/api-keys/shodan/deactivate")
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    r = await client.patch("/api/settings/api-keys/shodan/activate")
    assert r.status_code == 200
    assert r.json()["is_active"] is True


async def test_delete_api_key(client: AsyncClient):
    await client.post("/api/settings/api-keys", json={"service_name": "shodan", "key": "abc"})
    r = await client.delete("/api/settings/api-keys/shodan")
    assert r.status_code == 204


async def test_delete_api_key_not_found(client: AsyncClient):
    r = await client.delete("/api/settings/api-keys/nonexistent")
    assert r.status_code == 404


async def test_list_modules(client: AsyncClient):
    r = await client.get("/api/settings/modules")
    assert r.status_code == 200
    modules = r.json()
    names = [m["name"] for m in modules]
    assert "phone_lookup" in names
    assert "email_lookup" in names
    assert "domain_lookup" in names
    assert all(m["enabled"] is True for m in modules)


async def test_toggle_module(client: AsyncClient):
    r = await client.patch(
        "/api/settings/modules/phone_lookup",
        json={"name": "phone_lookup", "enabled": False},
    )
    assert r.status_code == 200
    assert r.json()["enabled"] is False

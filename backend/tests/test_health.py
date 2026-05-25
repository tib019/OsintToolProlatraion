from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

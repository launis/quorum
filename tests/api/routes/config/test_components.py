import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_components_empty(client: AsyncClient):
    # Real DB is empty initially (fresh temp file per session/fixture)
    response = await client.get("/v1/config/components")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_register_component(client: AsyncClient):
    payload = {
        "id": "test_agent",
        "name": "Test Agent",
        "type": "agent",
        "content": {"model": "gpt-4"} # Content is required
    }

    response = await client.post("/v1/config/components", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == "test_agent"

    # Verify retrieval
    get_res = await client.get("/v1/config/components/test_agent")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Test Agent"

@pytest.mark.asyncio
async def test_get_component_not_found(client: AsyncClient):
    response = await client.get("/v1/config/components/non_existent")
    assert response.status_code == 404

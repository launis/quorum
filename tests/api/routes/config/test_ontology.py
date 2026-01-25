import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_known_dimensions_success(client: AsyncClient):
    pass

@pytest.mark.asyncio
async def test_get_known_dimensions_no_defaults(client: AsyncClient):
    # Empty DB
    response = await client.get("/v1/config/ontology/dimensions")
    # Must fail with 404 ResourceNotFoundError if table empty
    assert response.status_code == 404
    assert response.status_code == 404
    data = response.json()
    assert "no-dimensions-found" in data["type"]

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_schema_workflow_definition(client: AsyncClient):
    response = await client.get("/v1/config/schemas/workflow_definition")
    assert response.status_code == 200
    schema = response.json()
    assert "title" in schema
    assert schema["title"] == "WorkflowDefinition"
    assert "properties" in schema
    assert "steps" in schema["properties"]

@pytest.mark.asyncio
async def test_get_schema_not_found(client: AsyncClient):
    response = await client.get("/v1/config/schemas/non_existent_model")
    assert response.status_code == 404
    assert response.status_code == 404
    data = response.json()
    assert "schema-not-found" in data["type"]

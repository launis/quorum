from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_component_repo, get_llm_handler
from backend_v2.tests.fakes.in_memory_repositories import InMemoryComponentRepository

app = FastAPI()


@app.get("/test-llm-dep")
async def route_test_llm_dep(llm_handler: Annotated[Any, Depends(get_llm_handler)]) -> Any:
    return {"has_repo": "repo" in dir(llm_handler)}


@pytest.mark.asyncio
async def test_llm_handler_dependency_injection() -> None:
    fake_repo = InMemoryComponentRepository()
    app.dependency_overrides[get_component_repo] = lambda: fake_repo

    with TestClient(app) as client:
        response = client.get("/test-llm-dep")
        assert response.status_code == 200
        assert response.json() == {"has_repo": True}

    app.dependency_overrides.clear()

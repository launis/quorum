from unittest.mock import AsyncMock
from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_llm_handler

app = FastAPI()


@app.get("/test-llm-dep")
async def route_test_llm_dep(llm_handler: Annotated[Any, Depends(get_llm_handler)]) -> Any:
    return {"has_repo": hasattr(llm_handler, "repo")}


@pytest.mark.asyncio
async def test_llm_handler_dependency_injection() -> None:
    # Override the repo dependency specifically for this test
    # Use a pure MagicMock to bypass strict Any ABC requirements
    from unittest.mock import MagicMock

    mock_repo = MagicMock(spec=Any)
    mock_repo._db = "mock_db_instance"

    from backend_v2.api.dependencies import get_db_driver

    app.dependency_overrides[get_db_driver] = lambda: mock_repo

    with TestClient(app) as client:
        response = client.get("/test-llm-dep")
        assert response.status_code == 200
        assert response.json() == {"has_repo": True}

    app.dependency_overrides.clear()

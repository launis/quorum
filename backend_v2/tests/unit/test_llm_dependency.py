import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_llm_handler, get_repo, LLMHandlerDep
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.llm.handler import LLMHandler

app = FastAPI()

from typing import Any
from fastapi import Depends

@app.get("/test-llm-dep")
async def test_llm_dep(llm_handler: Any = Depends(get_llm_handler)):
    return {"has_repo": hasattr(llm_handler, "repo")}

@pytest.mark.asyncio
async def test_llm_handler_dependency_injection():
    # Override the repo dependency specifically for this test
    # Use a pure MagicMock to bypass strict AbstractWorkflowRepository ABC requirements
    from unittest.mock import MagicMock
    mock_repo = MagicMock(spec=AbstractWorkflowRepository)
    mock_repo._db = "mock_db_instance"
    
    app.dependency_overrides[get_repo] = lambda: mock_repo
    
    with TestClient(app) as client:
        response = client.get("/test-llm-dep")
        assert response.status_code == 200
        assert response.json() == {"has_repo": True}
    
    app.dependency_overrides.clear()

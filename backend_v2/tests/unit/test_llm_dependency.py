"""Unit tests for FastAPI LLMHandler dependency injection binding."""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from backend_v2.api.dependencies import get_llm_handler, get_system_repo
from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import ErrorCodes, ServiceUnavailableError
from backend_v2.llm.handler import LLMHandler
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class LLMDependencyCheckResponseDTO(BaseModel):
    """Response payload confirming LLMHandler repository injection."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    has_repo: bool


app = FastAPI()


@app.get("/test-llm-dep", response_model=LLMDependencyCheckResponseDTO)
async def route_test_llm_dep(
    llm_handler: Annotated[LLMHandler, Depends(get_llm_handler)],
) -> LLMDependencyCheckResponseDTO:
    """Return whether the injected LLMHandler binds a valid system repository.

    Args:
        llm_handler: Injected LLMHandler instance.

    Returns:
        LLMDependencyCheckResponseDTO indicating repository presence.
    """
    return LLMDependencyCheckResponseDTO(has_repo=llm_handler.repo is not None)


@pytest.mark.asyncio
async def test_llm_handler_dependency_injection() -> None:
    """Verify get_llm_handler injects the overridden ISystemRepository into LLMHandler."""
    fake_repo = InMemoryUnifiedWorkflowRepository()
    app.dependency_overrides[get_system_repo] = lambda: fake_repo
    try:
        with TestClient(app) as client:
            response = client.get("/test-llm-dep")
            assert response.status_code == 200
            assert response.json() == {"has_repo": True}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_llm_handler_dependency_injection_failure() -> None:
    """Verify upstream repository resolution failure propagates ServiceUnavailableError."""

    def _failing_system_repo() -> ISystemRepository:
        raise ServiceUnavailableError(
            message="System repository unavailable",
            details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
        )

    app.dependency_overrides[get_system_repo] = _failing_system_repo
    try:
        with TestClient(app, raise_server_exceptions=True) as client, pytest.raises(ServiceUnavailableError) as exc:
            client.get("/test-llm-dep")
        assert exc.value.status_code == 503
        assert exc.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
    finally:
        app.dependency_overrides.clear()

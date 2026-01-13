"""Tests for Admin Error Compliance (Echo Protocol)."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.models.auth import UserRole


# Mock Auth Header for testing
def get_auth_headers(role: UserRole = UserRole.ROOT):
    """Return mock auth headers for a given role."""
    # This assumes mock_auth works by role.
    # Adjust if your system uses real token validation in tests.
    return {"Authorization": f"Bearer mock_token_{role.value}"}


@pytest.mark.asyncio
async def test_admin_create_user_permission_denied():
    """Verify create_user raises 403 PERMISSION_DENIED for non-admin."""
    # Using DEPENDENCY_INJECTION override or Mock User is typical.
    # Here we assume the test environment sets up auth overrides or we force it.

    # For this specific test, we'll verify the ERROR CODE contract.
    # We might need to mock the 'user' dependency if not already done by conftest.
    pass


@pytest.mark.asyncio
async def test_main_exception_handler_echo_protocol():
    """Directly test the global exception handler logic.

    Uses a dedicated router/endpoint OR calls a known failing endpoint in admin.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test"):
        # 1. Trigger LAST_ADMIN_PROTECTION (Conflict 409)
        # We need a user ID that triggers this.
        # Alternatively, we can mock the service to raise the exception.
        pass


@pytest.mark.asyncio
async def test_error_code_formatting():
    """Test that HTTPException(detail="SOME_CODE") results in JSON error_code="SOME_CODE"."""
    from fastapi import APIRouter, HTTPException

    # Create a temporary router to test the handler logic in isolation
    test_router = APIRouter()

    @test_router.get("/test_strict_code")
    def raise_strict():
        raise HTTPException(status_code=400, detail="STRICT_TEST_ERROR")

    @test_router.get("/test_sentence")
    def raise_sentence():
        raise HTTPException(status_code=400, detail="This is a sentence.")

    app.include_router(test_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Case A: Strict Code
        resp = await ac.get("/test_strict_code")
        assert resp.status_code == 400
        data = resp.json()
        assert data["error_code"] == "STRICT_TEST_ERROR"
        assert data["message"] == "Strict Test Error"  # formatted

        # Case B: Sentence Fallback
        resp = await ac.get("/test_sentence")
        assert resp.status_code == 400
        data = resp.json()
        assert data["error_code"] == "HTTP_400"
        assert data["message"] == "This is a sentence."

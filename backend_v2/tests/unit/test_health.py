"""Unit tests for System Health API Router."""

from unittest.mock import patch

import pytest
from fastapi import status

from backend_v2.api.routers.system.health import get_system_hooks
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix


@pytest.fixture
def mock_current_user() -> TokenData:
    """Create a canonical admin user token fixture.

    Returns:
        A valid admin TokenData instance with a canonical Opaque Stripe ID.
    """
    return TokenData(id=generate_opaque_id(EntityPrefix.USER), role=UserRole.ADMIN)


@pytest.mark.asyncio
async def test_get_system_hooks_returns_sorted_hooks(mock_current_user: TokenData) -> None:
    """Verify get_system_hooks returns registered hook identifiers in sorted ascending order."""
    assert mock_current_user.role == UserRole.ADMIN
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.return_value = ["hook_z", "hook_a", "hook_m"]
        res = await get_system_hooks()
        assert res.hooks == ["hook_a", "hook_m", "hook_z"]


@pytest.mark.asyncio
async def test_get_system_hooks_empty_boundary() -> None:
    """Verify get_system_hooks handles an empty hook registry boundary cleanly."""
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.return_value = []
        res = await get_system_hooks()
        assert res.hooks == []


@pytest.mark.asyncio
async def test_get_system_hooks_reraises_app_exception() -> None:
    """Verify get_system_hooks re-raises known AppException instances without wrapping."""
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.side_effect = ConfigurationError("Registry corrupted")
        with pytest.raises(ConfigurationError) as exc_info:
            await get_system_hooks()

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_get_system_hooks_translates_unexpected_error_to_app_exception() -> None:
    """Verify unexpected runtime exceptions are logged and translated into RFC 7807 AppException."""
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.side_effect = RuntimeError("Unexpected registry failure")
        with pytest.raises(AppException) as exc_info:
            await get_system_hooks()

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


@pytest.mark.asyncio
async def test_get_system_hooks_rejects_invalid_hook_element_types() -> None:
    """Verify non-string hook items trigger strict Pydantic validation failure wrapped as AppException."""
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.return_value = [123, 456]
        with pytest.raises(AppException) as exc_info:
            await get_system_hooks()

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

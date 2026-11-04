"""Unit tests for System Health API Router."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request, status

from backend_v2.api.routers.system.health import get_system_health, get_system_hooks
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import get_settings


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


@pytest.mark.asyncio
async def test_get_system_health() -> None:
    """Verify get_system_health returns status='ok' and Settings SSOT metadata when state is initialized."""
    test_app = FastAPI()
    test_app.state.pool_manager = object()
    test_app.state.arq_pool = object()
    mock_request = MagicMock(spec=Request)
    mock_request.app = test_app

    cfg = get_settings()
    res = await get_system_health(mock_request)
    assert res.status == "ok"
    assert res.version == cfg.app_version
    assert res.environment == cfg.environment
    assert res.storage_backend == cfg.active_backend.value
    assert res.gcp_region == cfg.gcp_region
    assert res.primary_domain == cfg.primary_domain


@pytest.mark.asyncio
async def test_get_system_health_degraded_when_state_uninitialized() -> None:
    """Verify get_system_health returns status='degraded' when pool_manager or arq_pool is missing or None."""
    # Case 1: Fresh app state with attributes unset
    uninitialized_app = FastAPI()
    mock_request_unset = MagicMock(spec=Request)
    mock_request_unset.app = uninitialized_app

    res_unset = await get_system_health(mock_request_unset)
    assert res_unset.status == "degraded"

    # Case 2: pool_manager initialized, arq_pool is None
    partial_app = FastAPI()
    partial_app.state.pool_manager = object()
    partial_app.state.arq_pool = None
    mock_request_partial = MagicMock(spec=Request)
    mock_request_partial.app = partial_app

    res_partial = await get_system_health(mock_request_partial)
    assert res_partial.status == "degraded"


@pytest.mark.asyncio
async def test_get_system_health_failure_raises_app_exception() -> None:
    """Verify get_system_health re-raises AppException and translates unexpected errors into AppException."""
    test_app = FastAPI()
    mock_request = MagicMock(spec=Request)
    mock_request.app = test_app

    with patch(
        "backend_v2.api.routers.system.health.get_settings",
        side_effect=ConfigurationError("Invalid backend"),
    ):
        with pytest.raises(ConfigurationError):
            await get_system_health(mock_request)

    with patch(
        "backend_v2.api.routers.system.health.get_settings",
        side_effect=RuntimeError("Settings failure"),
    ):
        with pytest.raises(AppException) as exc_info:
            await get_system_health(mock_request)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

"""Unit tests for canonical Users IAM API Router (backend_v2/api/routers/iam/users.py)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.iam.users import (
    create_user,
    delete_user,
    get_all_users,
    get_user,
    save_user,
)
from backend_v2.exceptions import (
    AppException,
    ConflictError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale

ADMIN_ID = "usr_0195f3a0000070008000000000000010"
TARGET_ID = "usr_0195f3a0000070008000000000000020"
ORG_ID = "org_0195f3a0000070008000000000000010"


@pytest.fixture
def mock_current_user() -> TokenData:
    """Provide an authenticated ADMIN TokenData fixture."""
    return TokenData(id=ADMIN_ID, role=UserRole.ADMIN, organization_id=ORG_ID)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """Provide an AsyncMock AuthService fixture."""
    return AsyncMock()


@pytest.fixture
def sample_user() -> User:
    """Provide a canonical User model fixture."""
    return User(
        id=TARGET_ID,
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_ID,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_users_router_crud_positive(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
    sample_user: User,
) -> None:
    """Positive: Verify get_all_users, get_user, create_user, save_user, and delete_user delegate to AuthService."""
    mock_auth_service.list_users.return_value = [sample_user]
    users = await get_all_users(current_user=mock_current_user, auth_service=mock_auth_service)
    assert users == [sample_user]

    mock_auth_service.get_user.return_value = sample_user
    fetched = await get_user(id=TARGET_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert fetched == sample_user

    create_payload = UserCreate(
        email="member@test.com",
        role=UserRole.MEMBER,
        organization_id=ORG_ID,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    mock_auth_service.create_user.return_value = sample_user
    created = await create_user(
        data=create_payload,
        current_user=mock_current_user,
        auth_service=mock_auth_service,
    )
    assert created == sample_user
    mock_auth_service.create_user.assert_awaited_once_with(ADMIN_ID, create_payload)

    update_payload = UserUpdate(name="Updated Name")
    mock_auth_service.update_user.return_value = sample_user
    saved = await save_user(
        id=TARGET_ID,
        data=update_payload,
        current_user=mock_current_user,
        auth_service=mock_auth_service,
    )
    assert saved == sample_user
    mock_auth_service.update_user.assert_awaited_once_with(ADMIN_ID, TARGET_ID, update_payload)

    mock_auth_service.delete_user.return_value = True
    deleted = await delete_user(id=TARGET_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert deleted.status == "success"
    assert deleted.id == TARGET_ID


@pytest.mark.asyncio
async def test_users_router_propagates_permission_denied_and_not_found_negative(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
) -> None:
    """Negative: Verify get_all_users and get_user propagate PermissionDeniedError and ResourceNotFoundError directly."""
    mock_auth_service.list_users.side_effect = PermissionDeniedError("Forbidden")
    with pytest.raises(PermissionDeniedError):
        await get_all_users(current_user=mock_current_user, auth_service=mock_auth_service)

    mock_auth_service.get_user.side_effect = ResourceNotFoundError("User", TARGET_ID)
    with pytest.raises(ResourceNotFoundError):
        await get_user(id=TARGET_ID, current_user=mock_current_user, auth_service=mock_auth_service)


@pytest.mark.asyncio
async def test_users_router_delete_error_branches_negative(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
) -> None:
    """Negative: Verify delete_user propagates AppException and wraps unexpected runtime errors in 500 AppException."""
    mock_auth_service.delete_user.side_effect = ConflictError("Last Admin Protection")
    with pytest.raises(ConflictError):
        await delete_user(id=TARGET_ID, current_user=mock_current_user, auth_service=mock_auth_service)

    mock_auth_service.delete_user.side_effect = RuntimeError("Database connection lost")
    with pytest.raises(AppException) as exc:
        await delete_user(id=TARGET_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert exc.value.status_code == 500

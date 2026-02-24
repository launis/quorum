from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status

from backend.exceptions import AppException, PermissionDeniedError
from backend.models.auth import UserCreate, UserRole

# Mock Dependencies
current_user_mock = MagicMock()
current_user_mock.role = UserRole.MEMBER
current_user_mock.id = "test-id"

root_user_mock = MagicMock()
root_user_mock.role = UserRole.ROOT
root_user_mock.id = "root-id"

auth_service_mock = AsyncMock()


@pytest.mark.asyncio
async def test_require_root_permission_denied():
    from backend.api.admin_router import require_root

    with pytest.raises(PermissionDeniedError) as exc:
        require_root(current_user_mock)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Root access required" in str(exc.value)


@pytest.mark.asyncio
async def test_require_admin_or_root_permission_denied():
    from backend.api.admin_router import require_admin_or_root

    with pytest.raises(PermissionDeniedError) as exc:
        require_admin_or_root(current_user_mock)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_user_fail_fast_permission():
    from backend.api.admin_router import create_user

    # Simulate AuthService raising PermissionError
    auth_service_mock.create_user.side_effect = PermissionError("Simulated Permission Error")

    with pytest.raises(PermissionDeniedError) as exc:
        await create_user(UserCreate(email="test@example.com", password="password"), root_user_mock, auth_service_mock)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Simulated Permission Error" in str(exc.value)


@pytest.mark.asyncio
async def test_create_user_fail_fast_value_error():
    from backend.api.admin_router import create_user

    # Simulate AuthService raising ValueError for invalid data
    auth_service_mock.create_user.side_effect = ValueError("Invalid User Data")

    with pytest.raises(AppException) as exc:
        await create_user(UserCreate(email="test@example.com", password="password"), root_user_mock, auth_service_mock)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid User Data" in str(exc.value)
    assert exc.value.details["error_code"] == "INVALID_USER_DATA"


@pytest.mark.asyncio
async def test_add_banned_phrase_validation():
    from backend.api.admin_router import BannedPhraseRequest, add_banned_phrase

    repo_mock = AsyncMock()

    # Too short (stripped)
    req = BannedPhraseRequest(phrase=" a ")

    with pytest.raises(AppException) as exc:
        await add_banned_phrase(req, repo_mock)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Phrase too short" in str(exc.value)

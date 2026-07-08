from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from backend_v2.api.dependencies import (
    get_auth_service,
    get_current_user_from_header,
    get_document_extraction_service,
    get_studio_simulation_service,
)
from backend_v2.exceptions import AuthenticationError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.settings import Settings


@pytest.fixture
def mock_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_settings() -> Any:
    return Settings(use_firebase_auth=False)


def test_get_auth_service(mock_repo: Any, mock_settings: Any) -> None:
    auth_service = get_auth_service(repo=mock_repo, settings=mock_settings)
    assert auth_service is not None


@pytest.mark.asyncio
async def test_get_current_user_from_header_missing_token() -> None:
    """Test get_current_user_from_header raises exception when token is missing."""
    mock_auth_service = AsyncMock()

    with pytest.raises(AuthenticationError) as exc:
        await get_current_user_from_header(auth_service=mock_auth_service, token=None)

    assert "Missing authentication token" in str(exc.value)


@pytest.mark.asyncio
async def test_get_current_user_from_header_valid_token() -> None:
    """Test get_current_user_from_header returns user data for valid token."""
    mock_auth_service = AsyncMock()
    expected_user = TokenData(id="usr_123", email="test@test.com", role=UserRole.MEMBER)
    mock_auth_service.verify_token.return_value = expected_user

    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "valid_token"

    user = await get_current_user_from_header(auth_service=mock_auth_service, token=mock_credentials)
    assert user == expected_user
    mock_auth_service.verify_token.assert_called_once_with("valid_token")


@pytest.mark.asyncio
async def test_get_studio_simulation_service(mock_repo: Any) -> None:
    """Test get_studio_simulation_service injection."""
    service = await get_studio_simulation_service(
        prompt_block_service=AsyncMock(),
    )  # noqa: E501
    assert service is not None
    assert service.prompt_block_service is not None


def test_get_document_extraction_service() -> None:
    """Test get_document_extraction_service."""
    service = get_document_extraction_service()
    assert service is not None

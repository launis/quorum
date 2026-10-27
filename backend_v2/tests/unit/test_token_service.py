"""Unit tests for token service and authentication token verification."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import jwt
import pytest

from backend_v2.exceptions import (
    AuthenticationError,
    ErrorCodes,
)
from backend_v2.models.auth import (
    User,
    UserRole,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import (
    JWT_ALGORITHM,
    JWT_SECRET,
    AuthService,
    TokenService,
    UserRepository,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_auth_service_verify_token_mock(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_1234abcd",
    )
    await mock_repo.create_user(test_user)
    token_data = await service.verify_token("mock-token:usr_1234abcd")

    assert token_data.id == "usr_1234abcd"
    assert token_data.role == UserRole.MEMBER


@pytest.mark.asyncio
async def test_auth_service_verify_token_mock_forbidden_in_production(
    mock_repo: InMemoryUnifiedWorkflowRepository, monkeypatch: Any
) -> None:
    from backend_v2.exceptions import AuthenticationError
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)
    service = AuthService(mock_repo, use_firebase=True)

    with pytest.raises(AuthenticationError) as exc_info:
        await service.verify_token("mock-token:usr_1234abcd")
    assert "Mock tokens are strictly forbidden in production" in exc_info.value.message


@pytest.mark.asyncio
async def test_auth_service_create_impersonation_token(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    token = service.create_impersonation_token("target_usr_123")
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_auth_service_init_firebase_fallback(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test AuthService fallback to mock when firebase is not installed."""
    with patch("backend_v2.services.auth.firebase_auth_module", None):
        auth = AuthService(mock_repo, use_firebase=True)
        assert auth.use_firebase is False


@pytest.mark.asyncio
async def test_auth_service_verify_token_impersonation_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test verify_token internal impersonation branches and errors."""
    auth = AuthService(mock_repo, use_firebase=False)
    test_user = User(
        id="usr_impersonated1",
        email="imp@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )

    # Valid impersonation token
    token = auth.create_impersonation_token("usr_impersonated1")
    await mock_repo.create_user(test_user)
    token_data = await auth.verify_token(token)
    assert token_data.id == "usr_impersonated1"
    assert token_data.role == UserRole.ADMIN

    # Missing sub claim
    bad_token = jwt.encode({"exp": time.time() + 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    with pytest.raises(AuthenticationError):
        await auth.verify_token(bad_token)

    # Impersonated user not found in DB
    await mock_repo.delete_user("usr_impersonated1")
    with pytest.raises(AuthenticationError) as exc_missing:
        await auth.verify_token(token)
    assert exc_missing.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED

    # Expired token
    expired_token = jwt.encode(
        {"sub": "usr_impersonated1", "exp": time.time() - 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    with pytest.raises(AuthenticationError) as exc_exp:
        await auth.verify_token(expired_token)
    assert exc_exp.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED

    # Invalid JWT token
    with pytest.raises(AuthenticationError) as exc_inv:
        await auth.verify_token("invalid.jwt.token")
    assert exc_inv.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


@pytest.mark.asyncio
async def test_auth_service_verify_token_mock_missing_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test verify_token in mock mode when user does not exist in DB."""
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)
    auth = AuthService(mock_repo, use_firebase=False)
    with pytest.raises(AuthenticationError) as excinfo:
        await auth.verify_token("mock-token:usr_nonexistent")
    assert excinfo.value.error_code == ErrorCodes.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_auth_service_verify_token_firebase_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test verify_token in Firebase mode."""
    mock_fb = MagicMock()
    auth = AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)

    test_user = User(
        id="usr_fbuser000123",
        email="fb@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=None,
    )

    # Case 1: User already in DB
    mock_fb.verify_id_token.return_value = {"uid": "usr_fbuser000123", "email": "fb@test.com"}
    await mock_repo.create_user(test_user)
    res = await auth.verify_token("valid_fb_token")
    assert res.id == "usr_fbuser000123"

    # Case 2: User not in DB -> Auto-registration
    await mock_repo.delete_user(test_user.id)
    res2 = await auth.verify_token("valid_fb_token")
    assert res2.id == "usr_fbuser000123"
    assert res2.role == UserRole.MEMBER
    assert (await mock_repo.get_user("usr_fbuser000123")) is not None

    # Case 3: User not in DB and missing email claim -> raises AuthenticationError
    await mock_repo.delete_user(test_user.id)
    mock_fb.verify_id_token.return_value = {"uid": "usr_fbuser000123"}
    with pytest.raises(AuthenticationError) as exc_no_email:
        await auth.verify_token("valid_fb_token_no_email")
    assert exc_no_email.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Case 4: verify_id_token raises exception
    mock_fb.verify_id_token.side_effect = RuntimeError("Firebase unreachable")
    with pytest.raises(AuthenticationError) as exc_fb_err:
        await auth.verify_token("broken_fb_token")
    assert exc_fb_err.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


def test_create_impersonation_token_generates_signed_jwt(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-01: create_impersonation_token returns valid signed JWT with sub and type."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    token = token_service.create_impersonation_token(target_id="usr_target12345678", duration_seconds=3600)
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert decoded["sub"] == "usr_target12345678"
    assert decoded["type"] == "impersonation"
    assert decoded["exp"] > time.time()


@pytest.mark.asyncio
async def test_verify_token_impersonation_token_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-02: verify_token with valid impersonation JWT returns TokenData matching user profile."""
    user_repo = UserRepository(mock_repo)
    token_service = TokenService(repo=user_repo, use_firebase=False)
    user = User(
        id="usr_imptarget0001",
        email="imptarget@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    await mock_repo.create_user(user)

    token = token_service.create_impersonation_token(target_id="usr_imptarget0001", duration_seconds=3600)
    token_data = await token_service.verify_token(token)

    assert token_data.id == "usr_imptarget0001"
    assert token_data.role == UserRole.ADMIN
    assert token_data.email == "imptarget@test.com"
    assert token_data.organization_id == "org_test00000001"


@pytest.mark.asyncio
async def test_verify_token_impersonation_missing_sub_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-03: verify_token with signed JWT missing sub raises AUTHENTICATION_FAILED."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    bad_token = jwt.encode({"exp": time.time() + 3600, "type": "impersonation"}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token(bad_token)
    assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


@pytest.mark.asyncio
async def test_verify_token_impersonation_user_not_found_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-04: verify_token with sub pointing to non-existent user raises AUTH_TOKEN_EXPIRED."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    token = token_service.create_impersonation_token(target_id="usr_nonexistent001", duration_seconds=3600)

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token(token)
    assert exc_info.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED


@pytest.mark.asyncio
async def test_verify_token_expired_jwt_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-05: verify_token with expired JWT timestamp raises AUTH_TOKEN_EXPIRED."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    expired_token = jwt.encode(
        {"sub": "usr_target00000001", "exp": time.time() - 3600, "type": "impersonation"},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token(expired_token)
    assert exc_info.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED


@pytest.mark.asyncio
async def test_verify_token_invalid_jwt_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-06: verify_token with malformed or tampered token raises AUTHENTICATION_FAILED."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token("malformed.tampered.token")
    assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


@pytest.mark.asyncio
async def test_verify_token_mock_token_in_production_forbidden_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-P2-07: verify_token with mock token when allow_mock_tokens is False raises PERMISSION_DENIED."""
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token("mock-token:usr_test00000001")
    assert exc_info.value.error_code == ErrorCodes.PERMISSION_DENIED
    assert "Mock tokens are strictly forbidden in production" in exc_info.value.message


@pytest.mark.asyncio
async def test_verify_token_mock_token_user_not_found_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-P2-08: verify_token with mock token for missing user raises PERMISSION_DENIED."""
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token("mock-token:usr_missing000001")
    assert exc_info.value.error_code == ErrorCodes.PERMISSION_DENIED
    assert "Mock User not found for ID" in exc_info.value.message


@pytest.mark.asyncio
async def test_verify_token_mock_token_success_returns_tokendata(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-P2-09: verify_token with mock token for existing user returns TokenData matching profile."""
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    user = User(
        id="usr_mockexists001",
        email="mockexists@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    await mock_repo.create_user(user)

    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    token_data = await token_service.verify_token("mock-token:usr_mockexists001")

    assert token_data.id == "usr_mockexists001"
    assert token_data.role == UserRole.MEMBER
    assert token_data.email == "mockexists@test.com"
    assert token_data.organization_id == "org_test00000001"


@pytest.mark.asyncio
async def test_verify_token_firebase_token_success_returns_tokendata(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-10: verify_token with valid Firebase token and existing user returns TokenData."""
    user = User(
        id="usr_fbexist000001",
        email="fbexist@test.com",
        role=UserRole.MANAGER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    await mock_repo.create_user(user)

    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=True)
    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {"uid": "usr_fbexist000001", "email": "fbexist@test.com"}
    token_service.firebase_auth = mock_fb

    token_data = await token_service.verify_token("valid_firebase_jwt_token")

    assert token_data.id == "usr_fbexist000001"
    assert token_data.role == UserRole.MANAGER
    assert token_data.email == "fbexist@test.com"
    assert token_data.organization_id == "org_test00000001"


@pytest.mark.asyncio
async def test_verify_token_firebase_auto_registration_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-11: verify_token with Firebase token for non-existing user auto-registers as MEMBER."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=True)
    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {"uid": "usr_fbnewauto0001", "email": "autoreg@test.com"}
    token_service.firebase_auth = mock_fb

    token_data = await token_service.verify_token("valid_firebase_jwt_token")

    assert token_data.id == "usr_fbnewauto0001"
    assert token_data.role == UserRole.MEMBER
    assert token_data.email == "autoreg@test.com"
    assert token_data.organization_id is None

    stored_user = await mock_repo.get_user("usr_fbnewauto0001")
    assert stored_user is not None
    assert stored_user.role == UserRole.MEMBER
    assert stored_user.email == "autoreg@test.com"


@pytest.mark.asyncio
async def test_verify_token_firebase_missing_email_raises_authentication_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P2-12: verify_token with Firebase token missing email for non-existing user raises AUTHENTICATION_FAILED."""
    token_service = TokenService(repo=UserRepository(mock_repo), use_firebase=True)
    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {"uid": "usr_fbnoemail0001"}
    token_service.firebase_auth = mock_fb

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.verify_token("valid_firebase_jwt_no_email")
    assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED
    assert "missing email claim" in exc_info.value.message

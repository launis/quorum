import time
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from pydantic import ValidationError

from backend_v2.api.routers.iam.auth import get_my_profile, list_available_roles, list_users
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import (
    JWT_ALGORITHM,
    JWT_SECRET,
    LEGACY_ROOT_MASTER_ID,
    LEGACY_SYSTEM_ORG_ID,
    SYSTEM_ROOT_USER_ID,
    AuthService,
    OrganizationRepository,
    OrganizationService,
    TokenService,
    UserRepository,
    UserService,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_organization_repository(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    org_repo = OrganizationRepository(mock_repo)

    test_org = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )

    # Test get_by_id
    await mock_repo.create_organization(test_org)
    org = await org_repo.get_by_id("org_1234abcd")
    assert org is not None
    assert org.id == "org_1234abcd"

    # Test create
    org_obj = Organization(
        id="org_2345bcde",
        name="New Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(org_obj)
    persisted = await mock_repo.get_organization("org_2345bcde")
    assert persisted is not None

    # Test list_all
    orgs = await org_repo.list_all()
    assert len(orgs) == 2


@pytest.mark.asyncio
async def test_user_repository(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    user_repo = UserRepository(mock_repo)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_1234abcd",
    )

    # Test get_by_id
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_id("usr_1234abcd")
    assert user is not None
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_user_repository_create_update_delete(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    user_repo = UserRepository(mock_repo)

    # create
    new_user = User(
        id="usr_2345bcde",
        email="new@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_2345bcde",
    )
    await user_repo.create(new_user)
    persisted = await mock_repo.get_user("usr_2345bcde")
    assert persisted is not None

    # update
    updated = await user_repo.update("usr_2345bcde", UserUpdate(name="Updated Name"))
    assert updated is not None
    assert updated.name == "Updated Name"

    # delete
    result = await user_repo.delete("usr_2345bcde")
    assert result is True
    assert await mock_repo.get_user("usr_2345bcde") is None


# --- Phase 1 Test Contracts (TC-P1-01 to TC-P1-13) ---


@pytest.mark.asyncio
async def test_organization_repository_get_by_id_found_returns_organization(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_test1234",
        name="Test Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    res = await org_repo.get_by_id("org_test1234")
    assert res is not None
    assert res.id == "org_test1234"
    assert res.name == "Test Org"


@pytest.mark.asyncio
async def test_organization_repository_get_by_id_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    res = await org_repo.get_by_id("org_missing")
    assert res is None


@pytest.mark.asyncio
async def test_organization_repository_create_persists_and_returns(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_create123",
        name="Created Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    created = await org_repo.create(test_org)
    assert created.id == "org_create123"
    persisted = await mock_repo.get_organization("org_create123")
    assert persisted is not None


@pytest.mark.asyncio
async def test_organization_repository_list_all_returns_list(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_list1234",
        name="List Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(test_org)
    orgs = await org_repo.list_all()
    assert isinstance(orgs, list)
    assert any(o.id == "org_list1234" for o in orgs)


@pytest.mark.asyncio
async def test_user_repository_get_by_id_found_returns_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_abc12345",
        email="abc@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_id("usr_abc12345")
    assert user is not None
    assert user.id == "usr_abc12345"


@pytest.mark.asyncio
async def test_user_repository_get_by_id_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user = await user_repo.get_by_id("usr_none123")
    assert user is None


@pytest.mark.asyncio
async def test_user_repository_get_by_email_found_returns_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_email123",
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_email("admin@example.com")
    assert user is not None
    assert user.id == "usr_email123"


@pytest.mark.asyncio
async def test_user_repository_get_by_email_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user = await user_repo.get_by_email("unknown@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_user_repository_create_duplicate_id_raises_app_exception(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_dup12345",
        email="dup1@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    dup_user = User(
        id="usr_dup12345",
        email="dup2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    with pytest.raises(AppException) as exc_info:
        await user_repo.create(dup_user)
    assert exc_info.value.status_code == 409
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value


@pytest.mark.asyncio
async def test_user_repository_update_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    res = await user_repo.update("usr_missing", UserUpdate(name="New Name"))
    assert res is None


@pytest.mark.asyncio
async def test_user_repository_update_success_returns_updated_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_upd12345",
        email="upd@test.com",
        name="Original Name",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    updated = await user_repo.update("usr_upd12345", UserUpdate(name="Updated Name"))
    assert updated is not None
    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_user_repository_delete_calls_underlying_repo(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_del12345",
        email="del@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    res = await user_repo.delete("usr_del12345")
    assert res is True
    assert await user_repo.get_by_id("usr_del12345") is None


@pytest.mark.asyncio
async def test_user_repository_get_by_organization_filters_and_validates(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user1 = User(
        id="usr_org12301",
        email="user1@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_target01",
    )
    user2 = User(
        id="usr_org12302",
        email="user2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_target01",
    )
    user_other = User(
        id="usr_orgother01",
        email="other@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_other01",
    )
    await user_repo.create(user1)
    await user_repo.create(user2)
    await user_repo.create(user_other)

    users = await user_repo.get_by_organization("org_target01")
    assert len(users) == 2
    assert all(isinstance(u, User) for u in users)
    assert {u.id for u in users} == {"usr_org12301", "usr_org12302"}


@pytest.mark.asyncio
async def test_auth_service_init(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)
    assert service.use_firebase is False


@pytest.mark.asyncio
async def test_auth_service_verify_token_mock(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
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
        storage_backend="LOCAL",
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
async def test_auth_service_list_users(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    u1 = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    u2 = User(
        id="usr_2345bcde",
        email="test2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_2345bcde",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )

    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)

    initiator = TokenData(id="admin_1234abcd", role=UserRole.ROOT, email="root@test.com")
    users = await service.list_users(initiator)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_auth_service_get_user(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator = TokenData(id="root_1234abcd", role=UserRole.ROOT, email="root@test.com")
    user = await service.get_user(initiator, "usr_1234abcd")
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_auth_service_tenant_isolation(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_target12",
        email="target@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_target12",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator_admin = TokenData(
        id="usr_admin123", role=UserRole.ADMIN, organization_id="org_target12", email="admin@test.com"
    )

    user = await service.get_user(initiator_admin, "usr_target12")
    assert user.id == "usr_target12"

    initiator_wrong_org = TokenData(
        id="usr_admin456", role=UserRole.ADMIN, organization_id="org_wrong123", email="admin2@test.com"
    )

    with pytest.raises(PermissionDeniedError):
        await service.get_user(initiator_wrong_org, "usr_target12")


# --- Auth Router Tests ---


@pytest.mark.asyncio
async def test_auth_router_list_roles() -> None:
    roles = await list_available_roles()
    assert "ROOT" in roles


@pytest.mark.asyncio
async def test_auth_router_get_my_profile(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)
    mock_user = User(
        id="usr_12345678",
        email="me@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        language="en",
        theme_mode="system",
        created_at="2026-01-01T00:00:00Z",
    )
    await mock_repo.create_user(mock_user)
    user = await get_my_profile(current_user=TokenData(id="usr_12345678", role=UserRole.MEMBER), auth_service=service)
    assert user == mock_user


@pytest.mark.asyncio
async def test_auth_router_list_users() -> None:
    mock_service = AsyncMock()
    mock_service.list_users.return_value = []
    users = await list_users(current_user=TokenData(id="usr_123", role=UserRole.MEMBER), auth_service=mock_service)
    assert users == []


def test_system_organizations_is_system() -> None:
    assert SystemOrganizations.is_system("org_system000000") is True
    assert SystemOrganizations.is_system("SYSTEM") is True
    assert SystemOrganizations.is_system(None) is True
    assert SystemOrganizations.is_system("") is True
    assert SystemOrganizations.is_system("org_e531d2ed8a6641f6") is False


def test_auth_models_validation_coverage() -> None:
    now = datetime.now(timezone.utc)
    # Organization with datetime object and valid fields
    org = Organization(
        id="org_test12345",
        name="Valid Name",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=5000,
        rpm_limit=10,
        created_at=now,
        contact_email="test@org.com",
        billing_id="bill_12345",
    )
    assert org.created_at == now

    # Organization validation failures
    with pytest.raises(ValidationError):
        Organization(
            id="org_test12345",
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=-5.0,
            tpm_limit=5000,
            rpm_limit=10,
        )

    with pytest.raises(ValidationError):
        Organization(
            id="   ",
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=5000,
            rpm_limit=10,
        )

    with pytest.raises(ValidationError):
        Organization(
            id="org_test12345",
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=5000,
            rpm_limit=10,
            contact_email="   ",
        )

    # User with datetime and valid created_by
    user = User(
        id="usr_test12345",
        email="user@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        language="en",
        theme_mode="dark",
        created_at=now,
        created_by="usr_admin1234",
        name="Valid User",
        organization_id="org_test12345",
    )
    assert user.created_at == now

    with pytest.raises(ValidationError):
        User(
            id="usr_test12345",
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language="en",
            theme_mode="dark",
            created_at=now,
            name="   ",
        )

    with pytest.raises(ValidationError):
        User(
            id="   ",
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language="en",
            theme_mode="dark",
            created_at=now,
        )

    with pytest.raises(ValidationError):
        User(
            id="usr_test12345",
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language="en",
            theme_mode="dark",
            created_at=now,
            created_by="   ",
        )

    # OrganizationCreate validation
    org_create = OrganizationCreate(
        name="Valid Name",
        admin_email="admin@test.com",
        admin_password="secretpassword",
        admin_name="Admin Name",
        tpm_limit=5000,
        rpm_limit=10,
    )
    assert org_create.name == "Valid Name"

    with pytest.raises(ValidationError):
        OrganizationCreate(
            name="   ",
            admin_email="admin@test.com",
            admin_password="secretpassword",
            admin_name="Admin Name",
            tpm_limit=5000,
            rpm_limit=10,
        )

    # TokenData validation
    token = TokenData(id="usr_1234", role=UserRole.ADMIN, organization_id="org_1234", email="a@b.com")
    assert token.id == "usr_1234"

    with pytest.raises(ValidationError):
        TokenData(id="   ", role=UserRole.ADMIN)

    with pytest.raises(ValidationError):
        TokenData(id="usr_1234", role=UserRole.ADMIN, organization_id="   ")


@pytest.mark.asyncio
async def test_organization_repository_not_found(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test get_by_id returns None when organization is not found."""
    org_repo = OrganizationRepository(mock_repo)
    res = await org_repo.get_by_id("org_missing")
    assert res is None


@pytest.mark.asyncio
async def test_user_repository_additional_coverage(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test UserRepository get_by_email, create duplicate conflict, update not found, and get_by_organization."""
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_existing1234",
        email="existing@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_1234abcd",
    )

    # get_by_email
    await mock_repo.create_user(test_user)
    found = await user_repo.get_by_email("existing@test.com")
    assert found is not None
    assert found.id == "usr_existing1234"

    # create duplicate raises conflict
    with pytest.raises(AppException) as excinfo:
        await user_repo.create(test_user)
    assert excinfo.value.status_code == 409

    # update when user not found returns None
    res = await user_repo.update("usr_unknown", UserUpdate(name="New Name"))
    assert res is None

    # get_by_organization
    users = await user_repo.get_by_organization("org_1234abcd")
    assert len(users) == 1
    assert users[0].id == test_user.id


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
) -> None:
    """Test verify_token in mock mode when user does not exist in DB."""
    auth = AuthService(mock_repo, use_firebase=False)
    with pytest.raises(AuthenticationError) as excinfo:
        await auth.verify_token("mock-token:usr_nonexistent")
    assert excinfo.value.error_code == ErrorCodes.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_auth_service_verify_token_firebase_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test verify_token in Firebase mode."""
    auth = AuthService(mock_repo, use_firebase=False)
    auth.use_firebase = True
    mock_fb = MagicMock()
    auth.firebase_auth = mock_fb

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


@pytest.mark.asyncio
async def test_auth_service_create_organization_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test create_organization permissions and success flow."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    payload = OrganizationCreate(
        name="New Acme",
        admin_email="admin@acme.com",
        admin_password="password123",
        admin_name="Acme Admin",
        tpm_limit=50000,
        rpm_limit=500,
    )

    # Non-root initiator raises PermissionDeniedError
    non_root_token = TokenData(id="usr_member000001", role=UserRole.ADMIN, email="admin@test.com")
    with pytest.raises(PermissionDeniedError):
        await auth.create_organization(non_root_token, payload)

    # ROOT initiator succeeds
    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    root_user = User(
        id="usr_root00000001",
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )
    await mock_repo.create_user(root_user)

    created_org = await auth.create_organization(root_token, payload)
    assert created_org.name == "New Acme"
    assert (await mock_repo.get_organization(created_org.id)) is not None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_create_user_hierarchy_and_validations(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test create_user permissions, hierarchy constraints, and organization validations."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    creator_admin = User(
        id="usr_creatoradmin01",
        email="creator@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_myorganization1",
    )
    mock_org = Organization(
        id="org_myorganization1",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )

    # 1. Creator not found
    with pytest.raises(AppException) as exc_nf:
        await auth.create_user(
            "usr_missing00001",
            UserCreate(
                email="u@test.com",
                role=UserRole.MEMBER,
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )
    assert exc_nf.value.status_code == 404

    # Seed creator_admin for subsequent steps (mock_org not seeded yet)
    await mock_repo.create_user(creator_admin)

    # 2. Non-root creating user in foreign organization
    with pytest.raises(PermissionDeniedError):
        await auth.create_user(
            "usr_creatoradmin01",
            UserCreate(
                email="u@test.com",
                role=UserRole.MEMBER,
                organization_id="org_otherorg0001",
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )

    # 3. Non-system org creating ROOT user
    with pytest.raises(PermissionDeniedError):
        await auth.create_user(
            "usr_creatoradmin01",
            UserCreate(
                email="u@test.com",
                role=UserRole.ROOT,
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )

    # 4. Target organization does not exist
    with pytest.raises(AppException) as exc_org_missing:
        await auth.create_user(
            "usr_creatoradmin01",
            UserCreate(
                email="u@test.com",
                role=UserRole.MEMBER,
                organization_id="org_myorganization1",
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )
    assert exc_org_missing.value.error_code == ErrorCodes.VALIDATION_FAILED

    # Seed mock_org now so organization exists for remaining steps
    await mock_repo.create_organization(mock_org)

    # 5. Role Hierarchy enforcement: ADMIN cannot create ROOT
    with pytest.raises(PermissionDeniedError):
        auth._enforce_hierarchy(creator_admin, UserRole.ROOT)

    # 6. Role Hierarchy enforcement: MANAGER cannot create users
    creator_manager = creator_admin.model_copy(update={"role": UserRole.MANAGER})
    with pytest.raises(PermissionDeniedError):
        auth._enforce_hierarchy(creator_manager, UserRole.MEMBER)

    # 7. Role Hierarchy enforcement: MEMBER cannot create users
    creator_member = creator_admin.model_copy(update={"role": UserRole.MEMBER})
    with pytest.raises(PermissionDeniedError):
        auth._enforce_hierarchy(creator_member, UserRole.MEMBER)

    # 8. Valid creation succeeds with audit logging
    new_user = await auth.create_user(
        "usr_creatoradmin01",
        UserCreate(
            email="member@test.com",
            role=UserRole.MEMBER,
            organization_id="org_myorganization1",
            name="Member User",
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        ),
    )
    assert new_user.email == "member@test.com"
    assert (await mock_repo.get_user(new_user.id)) is not None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_create_user_firebase_flow(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test create_user with Firebase enabled and fallback."""
    auth = AuthService(mock_repo, use_firebase=False)
    auth.use_firebase = True
    mock_fb = MagicMock()
    auth.firebase_auth = mock_fb

    creator_root = User(
        id="usr_rootcreator01",
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )
    await mock_repo.create_user(creator_root)
    await mock_repo.create_organization(
        Organization(
            id=SystemOrganizations.ROOT_SYSTEM,
            name="Root Org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
        )
    )

    # Firebase user created successfully
    mock_fb_user = MagicMock()
    mock_fb_user.id = "usr_fbnewuid1234"
    mock_fb.create_user.return_value = mock_fb_user

    created = await auth.create_user(
        "usr_rootcreator01",
        UserCreate(
            email="new_fb@test.com",
            password="password123",
            role=UserRole.MEMBER,
            name="FB User",
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        ),
    )
    assert created.id == "usr_fbnewuid1234"

    # Firebase user exists fallback
    mock_fb.create_user.side_effect = RuntimeError("Email already exists")
    existing_fb = MagicMock()
    existing_fb.id = "usr_fbexisting01"
    mock_fb.get_user_by_email.return_value = existing_fb

    created_existing = await auth.create_user(
        "usr_rootcreator01",
        UserCreate(
            email="existing_fb@test.com",
            password="password123",
            role=UserRole.MEMBER,
            name="FB Existing",
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        ),
    )
    assert created_existing.id == "usr_fbexisting01"

    # Firebase creation completely fails
    mock_fb.get_user_by_email.side_effect = RuntimeError("Network error")
    with pytest.raises(AppException) as exc_fb:
        await auth.create_user(
            "usr_rootcreator01",
            UserCreate(
                email="broken_fb@test.com",
                password="password123",
                role=UserRole.MEMBER,
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )
    assert exc_fb.value.status_code == 500


@pytest.mark.asyncio
async def test_auth_service_delete_user_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test delete_user access control, protections, and cascading deletion."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    initiator_admin = User(
        id="usr_admin000001",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    target_member = User(
        id="usr_member000001",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.delete_user("usr_admin000001", "usr_member000001")
    assert exc_nf.value.status_code == 404

    # Seed initiator_admin and target_member
    await mock_repo.create_user(initiator_admin)
    await mock_repo.create_user(target_member)

    # 2. Admin cannot delete users from other organizations
    target_foreign = target_member.model_copy(update={"id": "usr_foreign0001", "organization_id": "org_foreign00001"})
    await mock_repo.create_user(target_foreign)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_admin000001", "usr_foreign0001")

    # 3. Member cannot delete users
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_member000001", "usr_member000001")

    # 4. Root accounts cannot be deleted
    root_acc1 = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=initiator_admin.organization_id,
    )
    root_acc2 = User.model_construct(
        id=LEGACY_ROOT_MASTER_ID,
        email="legacy_root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=initiator_admin.organization_id,
    )
    await mock_repo.create_user(root_acc1)
    await mock_repo.create_user(root_acc2)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_admin000001", SYSTEM_ROOT_USER_ID)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_admin000001", LEGACY_ROOT_MASTER_ID)

    # 5. Last Admin Protection: cannot delete last admin of org
    target_admin = initiator_admin.model_copy(update={"id": "usr_targetadmin01"})
    await mock_repo.create_user(target_admin)
    # Remove initiator_admin so target_admin is the ONLY admin in org_test00000001
    await mock_repo.delete_user("usr_admin000001")
    # Call with root user as initiator
    with pytest.raises(ConflictError) as exc_last_admin:
        await auth.delete_user(SYSTEM_ROOT_USER_ID, "usr_targetadmin01")
    assert exc_last_admin.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 6. Successful delete with multiple admins and audit
    await mock_repo.create_user(initiator_admin)
    # Now there are 2 admins in org_test00000001 (initiator_admin and target_admin)
    deleted = await auth.delete_user("usr_admin000001", "usr_member000001")
    assert deleted is True
    assert (await mock_repo.get_user("usr_member000001")) is None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_delete_organization_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test delete_organization permissions, protection, empty vs non-empty force delete."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    non_root_token = TokenData(id="usr_admin000001", role=UserRole.ADMIN, email="admin@test.com")

    # 1. Non-root cannot delete organization
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(non_root_token, "org_target000001")

    # 2. Cannot delete system organizations
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, SystemOrganizations.ROOT_SYSTEM)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, LEGACY_SYSTEM_ORG_ID)

    # 3. Non-empty organization without force raises ConflictError
    member = User(
        id="usr_member000001",
        email="m@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_target000001",
    )
    await mock_repo.create_organization(
        Organization(
            id="org_target000001",
            name="Target Org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
        )
    )
    await mock_repo.create_user(member)

    with pytest.raises(ConflictError) as exc_not_empty:
        await auth.delete_organization(root_token, "org_target000001", force=False)
    assert exc_not_empty.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 4. Non-empty organization with force=True cascades user deletion and deletes org
    await auth.delete_organization(root_token, "org_target000001", force=True)
    assert (await mock_repo.get_user("usr_member000001")) is None
    assert (await mock_repo.get_organization("org_target000001")) is None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_update_user_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test update_user self-update, permissions, org transfer, last admin protection."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    admin_user = User(
        id="usr_admin000001",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    member_user = User(
        id="usr_member000001",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.update_user("usr_missing00001", "usr_member000001", UserUpdate(name="Name"))
    assert exc_nf.value.status_code == 404

    # Seed admin_user and member_user
    await mock_repo.create_user(admin_user)
    await mock_repo.create_user(member_user)

    # 2. Self-update: cannot change own role
    with pytest.raises(PermissionDeniedError):
        await auth.update_user("usr_member000001", "usr_member000001", UserUpdate(role=UserRole.ADMIN))

    # 3. Cross-org admin update denied
    foreign_member = member_user.model_copy(update={"id": "usr_foreign0001", "organization_id": "org_foreign00001"})
    await mock_repo.create_user(foreign_member)
    with pytest.raises(PermissionDeniedError):
        await auth.update_user("usr_admin000001", "usr_foreign0001", UserUpdate(name="New"))

    # 4. Member updating other user denied
    with pytest.raises(PermissionDeniedError):
        await auth.update_user("usr_member000001", "usr_admin000001", UserUpdate(name="New"))

    # 5. Non-root transferring user between orgs denied
    with pytest.raises(PermissionDeniedError):
        await auth.update_user("usr_admin000001", "usr_member000001", UserUpdate(organization_id="org_other0000001"))

    # 6. Demoting last admin of an organization denied
    # admin_user is currently the only admin in org_test00000001
    root_user = admin_user.model_copy(update={"id": "usr_root00000001", "role": UserRole.ROOT})
    await mock_repo.create_user(root_user)
    with pytest.raises(ConflictError) as exc_demote:
        await auth.update_user("usr_root00000001", "usr_admin000001", UserUpdate(role=UserRole.MEMBER))
    assert exc_demote.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 7. Update fails on repository level raises 500
    mock_repo.inject_fault("update_user", AppException("Update failed", status_code=500), trigger_count=1)
    with pytest.raises(AppException) as exc_up_fail:
        await auth.update_user("usr_admin000001", "usr_member000001", UserUpdate(name="Failing"))
    assert exc_up_fail.value.status_code == 500

    # 8. Successful update with audit logging
    res = await auth.update_user("usr_admin000001", "usr_member000001", UserUpdate(name="Updated Name"))
    assert res.name == "Updated Name"
    updated_in_store = await mock_repo.get_user("usr_member000001")
    assert updated_in_store is not None
    assert updated_in_store.name == "Updated Name"
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_update_user_role_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test update_user_role access control, promotion limits, and last admin protection."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    admin_user = User(
        id="usr_admin000001",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    manager_user = User(
        id="usr_manager00001",
        email="manager@test.com",
        role=UserRole.MANAGER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )
    member_user = User(
        id="usr_member000001",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test00000001",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.update_user_role("usr_missing00001", "usr_member000001", UserRole.MANAGER)
    assert exc_nf.value.status_code == 404

    # Seed users
    await mock_repo.create_user(admin_user)
    await mock_repo.create_user(manager_user)
    await mock_repo.create_user(member_user)

    # 2. Lower role cannot modify higher privilege
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role("usr_member000001", "usr_admin000001", UserRole.MEMBER)

    # 3. Cannot promote to role higher than own
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role("usr_manager00001", "usr_member000001", UserRole.ADMIN)

    # 4. Admin managing user in other organization denied
    foreign_member = member_user.model_copy(update={"id": "usr_foreign0002", "organization_id": "org_foreign00001"})
    await mock_repo.create_user(foreign_member)
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role("usr_admin000001", "usr_foreign0002", UserRole.MANAGER)

    # 5. Last admin demotion denied
    with pytest.raises(ConflictError) as exc_last_admin:
        await auth.update_user_role("usr_admin000001", "usr_admin000001", UserRole.MEMBER)
    assert exc_last_admin.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 6. Update failure raises 500
    mock_repo.inject_fault("update_user", AppException("Update failed", status_code=500), trigger_count=1)
    with pytest.raises(AppException) as exc_fail:
        await auth.update_user_role("usr_admin000001", "usr_member000001", UserRole.MANAGER)
    assert exc_fail.value.status_code == 500

    # 7. Successful update
    res = await auth.update_user_role("usr_admin000001", "usr_member000001", UserRole.MANAGER)
    assert res.role == UserRole.MANAGER
    updated_in_store = await mock_repo.get_user("usr_member000001")
    assert updated_in_store is not None
    assert updated_in_store.role == UserRole.MANAGER
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_organization_read_and_update(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test list_organizations, get_organization, update_organization, and get_users_by_organization."""
    auth = AuthService(mock_repo, use_firebase=False)
    test_org = Organization(
        id="org_test00000001",
        name="Test Organization",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)

    # 1. list_organizations
    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    member_with_org = TokenData(
        id="usr_member000001", role=UserRole.MEMBER, email="m@test.com", organization_id="org_test00000001"
    )
    member_no_org = TokenData(
        id="usr_orphan000001", role=UserRole.MEMBER, email="orphan@test.com", organization_id=None
    )

    assert len(await auth.list_organizations(root_token)) == 1
    assert len(await auth.list_organizations(member_with_org)) == 1
    assert len(await auth.list_organizations(member_no_org)) == 0

    # 2. get_organization
    # Not found
    with pytest.raises(ResourceNotFoundError):
        await auth.get_organization(root_token, "org_missing00001")

    # Member accessing foreign organization
    foreign_org = test_org.model_copy(update={"id": "org_foreign00001", "name": "Foreign Org"})
    await mock_repo.create_organization(foreign_org)
    with pytest.raises(PermissionDeniedError):
        await auth.get_organization(member_with_org, "org_foreign00001")

    # Success
    found_org = await auth.get_organization(member_with_org, "org_test00000001")
    assert found_org.id == "org_test00000001"

    # 3. update_organization
    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(member_with_org, "org_test00000001", OrganizationUpdateDTO(name="New"))

    # Root update with OrganizationUpdateDTO
    updated = await auth.update_organization(root_token, "org_test00000001", OrganizationUpdateDTO(name="Updated Name"))
    assert updated.id == "org_test00000001"

    # Root update with OrganizationCreate
    create_dto = OrganizationCreate(
        name="Brand New",
        admin_email="a@b.com",
        admin_password="password123",
        admin_name="Brand New Admin",
        tpm_limit=50000,
        rpm_limit=500,
    )
    updated2 = await auth.update_organization(root_token, "org_test00000001", create_dto)
    assert updated2.id == "org_test00000001"

    # 4. get_users_by_organization
    users = await auth.get_users_by_organization("org_empty0000001")
    assert users == []


@pytest.mark.asyncio
async def test_auth_service_ensure_root_user_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test ensure_root_user bootstrap, missing root error, and drift repair."""
    auth = AuthService(mock_repo, use_firebase=False)
    system_org = Organization(
        id=SystemOrganizations.ROOT_SYSTEM,
        name="System Administration",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    root_user = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )

    # Case 1: Root user missing from DB raises ConfigurationError
    await mock_repo.create_organization(system_org)
    with pytest.raises(AppException) as exc_missing:
        await auth.ensure_root_user()
    assert exc_missing.value.error_code == ErrorCodes.CONFIGURATION_ERROR

    # Case 2: System org missing -> bootstraps system org, succeeds
    await mock_repo.delete_organization(SystemOrganizations.ROOT_SYSTEM)
    await mock_repo.create_user(root_user)
    res = await auth.ensure_root_user()
    assert res.id == SYSTEM_ROOT_USER_ID
    assert (await mock_repo.get_organization(SystemOrganizations.ROOT_SYSTEM)) is not None

    # Case 3: Root user has drifted organization -> updates organization to ROOT_SYSTEM
    drifted_root = root_user.model_copy(update={"organization_id": "org_drifted00001"})
    await mock_repo.create_user(drifted_root)
    res_fixed = await auth.ensure_root_user()
    assert res_fixed.organization_id == SystemOrganizations.ROOT_SYSTEM
    refreshed = await mock_repo.get_user(SYSTEM_ROOT_USER_ID)
    assert refreshed is not None
    assert refreshed.organization_id == SystemOrganizations.ROOT_SYSTEM

    # Case 4: Root user refresh fails -> raises 500
    mock_repo.inject_fault("update_user", AppException("Update failure", status_code=500), trigger_count=1)
    await mock_repo.create_user(drifted_root)
    with pytest.raises(AppException) as exc_refresh_fail:
        await auth.ensure_root_user()
    assert exc_refresh_fail.value.status_code == 500


# --- Phase 2: TokenService Test Contracts (TC-P2-01 to TC-P2-12) ---


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
        storage_backend="LOCAL",
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
        storage_backend="LOCAL",
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
        storage_backend="LOCAL",
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


# ============================================================================
# Phase 3: Organization Service Extraction Tests (TC-P3-01 to TC-P3-19)
# ============================================================================


@pytest.mark.asyncio
async def test_create_organization_root_initiator_success(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """TC-P3-01: ROOT initiator successfully creates organization and admin user."""
    auth_service = AuthService(mock_repo)
    root_user = User(
        id="usr_root0000000001",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id="org_system000000",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_name="Acme Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    org = await auth_service.create_organization(root_initiator, payload)

    assert org.name == "Acme Corp"
    assert org.id.startswith("org_")
    assert org.is_active is True
    persisted_org = await mock_repo.get_organization(org.id)
    assert persisted_org is not None
    assert persisted_org.name == "Acme Corp"

    admin_user = await mock_repo.get_user_by_email("admin@acme.com")
    assert admin_user is not None
    assert admin_user.role == UserRole.ADMIN
    assert admin_user.organization_id == org.id


@pytest.mark.asyncio
async def test_create_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-02: Non-ROOT initiator raises PermissionDeniedError when creating organization."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin000000001", role=UserRole.ADMIN, organization_id="org_test000000001")
    payload = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_name="Acme Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_organization(admin_initiator, payload)
    assert "Only ROOT can create organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_organization_logs_audit_event_when_audit_service_configured(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-03: create_organization logs ORG_CREATED audit event when audit_service is present."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    root_user = User(
        id="usr_root0000000001",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id="org_system000000",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Audit Org",
        admin_email="admin@audit.com",
        admin_name="Audit Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    org = await auth_service.create_organization(root_initiator, payload)

    assert mock_audit.log_event.call_count == 2
    actions = [call.kwargs["action"] for call in mock_audit.log_event.call_args_list]
    assert "ORG_CREATED" in actions
    assert "USER_CREATED" in actions

    org_created_call = next(c for c in mock_audit.log_event.call_args_list if c.kwargs["action"] == "ORG_CREATED")
    assert org_created_call.kwargs["actor_id"] == "usr_root0000000001"
    assert org_created_call.kwargs["organization_id"] == org.id
    assert org_created_call.kwargs["target_id"] == org.id


@pytest.mark.asyncio
async def test_get_organization_root_initiator_any_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-04: ROOT initiator can get any organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_target0000001",
        name="Target Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    org = await auth_service.get_organization(root_initiator, "org_target0000001")
    assert org.id == "org_target0000001"
    assert org.name == "Target Org"


@pytest.mark.asyncio
async def test_get_organization_same_org_member_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-05: Non-root member can view their own organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_member0000001",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    member_initiator = TokenData(id="usr_member0000001", role=UserRole.MEMBER, organization_id="org_member0000001")

    org = await auth_service.get_organization(member_initiator, "org_member0000001")
    assert org.id == "org_member0000001"
    assert org.name == "My Org"


@pytest.mark.asyncio
async def test_get_organization_foreign_org_member_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-06: Foreign org member cannot view another organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_foreign000001",
        name="Foreign Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    foreign_member = TokenData(id="usr_member0000002", role=UserRole.MEMBER, organization_id="org_other00000001")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.get_organization(foreign_member, "org_foreign000001")
    assert "You do not have permission to view this organization." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-07: Fetching non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.get_organization(root_initiator, "org_missing000001")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_missing000001"


@pytest.mark.asyncio
async def test_list_organizations_root_initiator_returns_all_orgs(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-08: ROOT initiator lists all organizations in the repository."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_all0000000001",
        name="Org 1",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    org2 = Organization(
        id="org_all0000000002",
        name="Org 2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    orgs = await auth_service.list_organizations(root_initiator)
    assert len(orgs) == 2
    assert {o.id for o in orgs} == {"org_all0000000001", "org_all0000000002"}


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_returns_own_org_only(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-09: Tenant initiator lists only their own organization."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_mine00000001",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    org2 = Organization(
        id="org_other00000001",
        name="Other Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_mine00000001")

    orgs = await auth_service.list_organizations(admin_initiator)
    assert len(orgs) == 1
    assert orgs[0].id == "org_mine00000001"


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_no_org_id_returns_empty_list(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-10: Tenant initiator with no organization_id returns empty list."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_some00000001",
        name="Some Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    member_no_org = TokenData(id="usr_noorg00000001", role=UserRole.MEMBER, organization_id=None)

    orgs = await auth_service.list_organizations(member_no_org)
    assert orgs == []


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_update_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-11: ROOT initiator updates organization with OrganizationUpdateDTO."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_update0000001",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name", tpm_limit=60000)

    updated = await auth_service.update_organization(root_initiator, "org_update0000001", dto)
    assert updated.id == "org_update0000001"
    assert updated.name == "New Name"
    assert updated.tpm_limit == 60000


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_create_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-12: ROOT initiator updates organization using OrganizationCreate payload."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_update0000002",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    create_dto = OrganizationCreate(
        name="Converted Name",
        admin_email="a@b.com",
        admin_name="Admin",
        admin_password="password",
        tpm_limit=70000,
        rpm_limit=700,
    )

    updated = await auth_service.update_organization(root_initiator, "org_update0000002", create_dto)
    assert updated.id == "org_update0000002"
    assert updated.name == "Converted Name"
    assert updated.tpm_limit == 70000


@pytest.mark.asyncio
async def test_update_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-13: Non-ROOT initiator raises PermissionDeniedError on update."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_test000000001")
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_organization(admin_initiator, "org_test000000001", dto)
    assert "Only ROOT can update organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-14: Updating non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.update_organization(root_initiator, "org_missing000001", dto)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_missing000001"


@pytest.mark.asyncio
async def test_delete_organization_root_empty_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-15: ROOT deletes empty organization successfully."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_delete0000001",
        name="Delete Me",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_delete0000001")

    persisted = await mock_repo.get_organization("org_delete0000001")
    assert persisted is None
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "ORG_DELETED"
    assert call_kwargs["organization_id"] == "org_delete0000001"


@pytest.mark.asyncio
async def test_delete_organization_non_root_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-16: Non-ROOT user raises PermissionDeniedError on delete organization."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_test000000001")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(admin_initiator, "org_test000000001")
    assert "Only ROOT can delete organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_organization_system_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-17: Deleting system organization raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(root_initiator, "system")
    assert "protected and CANNOT be deleted" in str(exc_info.value)

    with pytest.raises(PermissionDeniedError) as exc_info_legacy:
        await auth_service.delete_organization(root_initiator, LEGACY_SYSTEM_ORG_ID)
    assert "protected and CANNOT be deleted" in str(exc_info_legacy.value)


@pytest.mark.asyncio
async def test_delete_organization_non_empty_without_force_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-18: Non-empty organization deletion without force raises ConflictError."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_busy000000001",
        name="Busy Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_busy000000001",
        email="busy1@test.com",
        name="Busy 1",
        role=UserRole.MEMBER,
        organization_id="org_busy000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    user2 = User(
        id="usr_busy000000002",
        email="busy2@test.com",
        name="Busy 2",
        role=UserRole.MEMBER,
        organization_id="org_busy000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.delete_organization(root_initiator, "org_busy000000001", force=False)
    assert "Organization is not empty" in exc_info.value.message
    assert exc_info.value.details is not None
    assert exc_info.value.details["reason"] == "ORG_NOT_EMPTY"


@pytest.mark.asyncio
async def test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-19: Force deletion cascades delete to users in org and Firebase."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit, use_firebase=True)
    mock_fb = MagicMock()
    auth_service.firebase_auth = mock_fb

    org = Organization(
        id="org_force00000001",
        name="Force Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_cascade000001",
        email="cascade1@test.com",
        name="Cascade 1",
        role=UserRole.MEMBER,
        organization_id="org_force00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    user2 = User(
        id="usr_cascade000002",
        email="cascade2@test.com",
        name="Cascade 2",
        role=UserRole.MEMBER,
        organization_id="org_force00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_force00000001", force=True)

    assert await mock_repo.get_organization("org_force00000001") is None
    assert await mock_repo.get_user("usr_cascade000001") is None
    assert await mock_repo.get_user("usr_cascade000002") is None
    assert mock_fb.delete_user.call_count == 2
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "ORG_DELETED"
    assert call_kwargs["details"]["users_deleted"] == 2
    assert call_kwargs["details"]["force_used"] is True


@pytest.mark.asyncio
async def test_direct_organization_service_execution(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies direct instantiation and execution of OrganizationService."""
    org_repo = OrganizationRepository(mock_repo)
    user_repo = UserRepository(mock_repo)
    mock_audit = AsyncMock()
    mock_create_user = AsyncMock()

    service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        audit_service=mock_audit,
        create_user_fn=mock_create_user,
    )

    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Direct Org",
        admin_email="direct@org.com",
        admin_name="Direct Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    created = await service.create_organization(root_initiator, payload)
    assert created.name == "Direct Org"
    assert mock_create_user.call_count == 1

    fetched = await service.get_organization(root_initiator, created.id)
    assert fetched.id == created.id

    listed = await service.list_organizations(root_initiator)
    assert any(o.id == created.id for o in listed)

    updated = await service.update_organization(
        root_initiator, created.id, OrganizationUpdateDTO(name="Updated Direct")
    )
    assert updated.name == "Updated Direct"

    await service.delete_organization(root_initiator, created.id)
    assert await org_repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_organization_repository_update_and_delete(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies OrganizationRepository update and delete methods."""
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_repocrud00001",
        name="Repo CRUD",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(test_org)

    update_success = await org_repo.update("org_repocrud00001", OrganizationUpdateDTO(name="New Repo CRUD"))
    assert update_success is True
    refreshed = await org_repo.get_by_id("org_repocrud00001")
    assert refreshed is not None
    assert refreshed.name == "New Repo CRUD"

    del_success = await org_repo.delete("org_repocrud00001")
    assert del_success is True
    assert await org_repo.get_by_id("org_repocrud00001") is None


# ==============================================================================
# Phase 4 Test Contracts (TC-P4-01 through TC-P4-39)
# ==============================================================================


@pytest.mark.asyncio
async def test_create_user_root_creator_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-01: ROOT creator can create an ADMIN user in any org with audit logging."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_test00000001",
        name="Test Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_user = User(
        id="usr_root00000001",
        email="root@test.com",
        name="Root User",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)

    payload = UserCreate(
        email="newadmin@test.com",
        name="New Admin",
        role=UserRole.ADMIN,
        organization_id="org_test00000001",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    created = await auth_service.create_user("usr_root00000001", payload)
    assert created.email == "newadmin@test.com"
    assert created.role == UserRole.ADMIN
    assert created.organization_id == "org_test00000001"
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "USER_CREATED"
    assert call_kwargs["actor_id"] == "usr_root00000001"


@pytest.mark.asyncio
async def test_create_user_admin_creator_same_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-02: ADMIN creator creates MEMBER in same org."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_test00000002",
        name="Test Org 2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    admin_user = User(
        id="usr_admin0000001",
        email="admin@test.com",
        name="Admin User",
        role=UserRole.ADMIN,
        organization_id="org_test00000002",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="member@test.com",
        name="Member User",
        role=UserRole.MEMBER,
        organization_id="org_test00000002",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    created = await auth_service.create_user("usr_admin0000001", payload)
    assert created.email == "member@test.com"
    assert created.role == UserRole.MEMBER


@pytest.mark.asyncio
async def test_create_user_admin_creator_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-03: ADMIN creating user targeting a foreign org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin_user = User(
        id="usr_admin0000002",
        email="admin2@test.com",
        name="Admin 2",
        role=UserRole.ADMIN,
        organization_id="org_test00000003",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="foreign@test.com",
        name="Foreign User",
        role=UserRole.MEMBER,
        organization_id="org_foreign00001",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_admin0000002", payload)
    assert "Cannot create users in other organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_admin_creating_root_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-04: ADMIN attempting to create ROOT raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin_user = User(
        id="usr_admin0000003",
        email="admin3@test.com",
        name="Admin 3",
        role=UserRole.ADMIN,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="rootattempt@test.com",
        name="Root Attempt",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_admin0000003", payload)
    assert "Admins cannot create Roots." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_manager_creating_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-05: MANAGER attempting to create user raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    await mock_repo.create_organization(
        Organization(
            id="org_test00000005",
            name="Org Test 5",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=1000.0,
            tpm_limit=10000,
            rpm_limit=100,
        )
    )
    manager = User(
        id="usr_mgr0000000001",
        email="mgr@test.com",
        name="Manager",
        role=UserRole.MANAGER,
        organization_id="org_test00000005",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(manager)

    payload = UserCreate(
        email="sub@test.com",
        name="Subordinate",
        role=UserRole.MEMBER,
        organization_id="org_test00000005",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_mgr0000000001", payload)
    assert "Managers are Technical Leads and cannot manage users. Ask an Admin." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_member_creating_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-06: MEMBER attempting to create user raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    await mock_repo.create_organization(
        Organization(
            id="org_test00000006",
            name="Org Test 6",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=1000.0,
            tpm_limit=10000,
            rpm_limit=100,
        )
    )
    member = User(
        id="usr_mem0000000001",
        email="mem@test.com",
        name="Member",
        role=UserRole.MEMBER,
        organization_id="org_test00000006",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(member)

    payload = UserCreate(
        email="sub2@test.com",
        name="Sub2",
        role=UserRole.MEMBER,
        organization_id="org_test00000006",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_mem0000000001", payload)
    assert "This user role cannot create users" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_non_existent_creator_raises_app_exception_404(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-07: Creator not found raises AppException with 404 RESOURCE_NOT_FOUND."""
    auth_service = AuthService(mock_repo)
    payload = UserCreate(
        email="new@test.com",
        name="New",
        role=UserRole.MEMBER,
        organization_id="org_test00000007",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(AppException) as exc_info:
        await auth_service.create_user("usr_missing000001", payload)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_create_user_non_existent_target_org_raises_app_exception_404(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-08: Non-existent target org raises AppException 404 VALIDATION_FAILED."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_root00000002",
        email="root2@test.com",
        name="Root 2",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="user_no_org@test.com",
        name="No Org",
        role=UserRole.MEMBER,
        organization_id="org_nonexistent01",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(AppException) as exc_info:
        await auth_service.create_user("usr_root00000002", payload)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_create_user_root_role_in_non_system_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-09: Root role in non-system org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_root00000003",
        email="root3@test.com",
        name="Root 3",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="badroot@test.com",
        name="Bad Root",
        role=UserRole.ROOT,
        organization_id="org_other0000001",
        is_active=True,
        language="en",
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_root00000003", payload)
    assert "Root users can only be created within the System Organization." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_root_initiator_any_user_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-10: ROOT initiator can get any user."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_any0000000001",
        email="any@test.com",
        name="Any User",
        role=UserRole.MEMBER,
        organization_id="org_any000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    root_token = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    fetched = await auth_service.get_user(root_token, "usr_any0000000001")
    assert fetched.id == "usr_any0000000001"


@pytest.mark.asyncio
async def test_get_user_self_fetch_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-11: User can get themselves."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_self000000001",
        email="self@test.com",
        name="Self User",
        role=UserRole.MEMBER,
        organization_id="org_self00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    self_token = TokenData(id="usr_self000000001", role=UserRole.MEMBER, organization_id="org_self00000001")

    fetched = await auth_service.get_user(self_token, "usr_self000000001")
    assert fetched.id == "usr_self000000001"


@pytest.mark.asyncio
async def test_get_user_admin_same_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-12: ADMIN can get user in same org."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_memsame00001",
        email="same@test.com",
        name="Same Org User",
        role=UserRole.MEMBER,
        organization_id="org_common000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    admin_token = TokenData(id="usr_admsame00001", role=UserRole.ADMIN, organization_id="org_common000001")

    fetched = await auth_service.get_user(admin_token, "usr_memsame00001")
    assert fetched.id == "usr_memsame00001"


@pytest.mark.asyncio
async def test_get_user_foreign_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-13: Fetching user from foreign org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_foreign000001",
        email="foreign@test.com",
        name="Foreign User",
        role=UserRole.MEMBER,
        organization_id="org_two000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    initiator_token = TokenData(id="usr_init000000001", role=UserRole.MEMBER, organization_id="org_one000000001")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.get_user(initiator_token, "usr_foreign000001")
    assert "You do not have permission to view this user." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_not_found_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-14: Fetching non-existent user raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_token = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.get_user(root_token, "usr_missing000002")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_type"] == "user"
    assert exc_info.value.details["resource_id"] == "usr_missing000002"


@pytest.mark.asyncio
async def test_list_users_root_initiator_returns_all_users(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-15: ROOT initiator lists all users across organizations."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_list000000001",
        email="u1@test.com",
        name="U1",
        role=UserRole.MEMBER,
        organization_id="org_a00000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    u2 = User(
        id="usr_list000000002",
        email="u2@test.com",
        name="U2",
        role=UserRole.ADMIN,
        organization_id="org_b00000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)
    root_token = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    users = await auth_service.list_users(root_token)
    assert len(users) == 2
    assert {u.id for u in users} == {"usr_list000000001", "usr_list000000002"}


@pytest.mark.asyncio
async def test_list_users_tenant_initiator_returns_own_org_users_only(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-16: Tenant initiator lists only users in their own org."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_tenant0000001",
        email="t1@test.com",
        name="T1",
        role=UserRole.MEMBER,
        organization_id="org_target_tenant",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    u2 = User(
        id="usr_tenant0000002",
        email="t2@test.com",
        name="T2",
        role=UserRole.MEMBER,
        organization_id="org_other_tenant",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)
    initiator = TokenData(id="usr_tenant0000001", role=UserRole.MEMBER, organization_id="org_target_tenant")

    users = await auth_service.list_users(initiator)
    assert len(users) == 1
    assert users[0].id == "usr_tenant0000001"


@pytest.mark.asyncio
async def test_get_users_by_organization_returns_matching_users(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-17: get_users_by_organization retrieves matching users."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_byorg00000001",
        email="bo1@test.com",
        name="BO1",
        role=UserRole.MEMBER,
        organization_id="org_matching00001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(u1)

    matching = await auth_service.get_users_by_organization("org_matching00001")
    assert len(matching) == 1
    assert matching[0].id == "usr_byorg00000001"


@pytest.mark.asyncio
async def test_update_user_root_initiator_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-18: ROOT initiator updates user and emits audit event."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    user = User(
        id="usr_update0000001",
        email="up@test.com",
        name="Old Name",
        role=UserRole.MEMBER,
        organization_id="org_up0000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    root = User(
        id="usr_root00000004",
        email="root4@test.com",
        name="Root 4",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    await mock_repo.create_user(root)

    updated = await auth_service.update_user("usr_root00000004", "usr_update0000001", UserUpdate(name="New Name"))
    assert updated.name == "New Name"
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "USER_UPDATED"


@pytest.mark.asyncio
async def test_update_user_self_update_non_role_fields_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-19: User self-update for non-role fields succeeds."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_selfup0000001",
        email="selfup@test.com",
        name="Self Up",
        role=UserRole.MEMBER,
        organization_id="org_selfup000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)

    updated = await auth_service.update_user(
        "usr_selfup0000001", "usr_selfup0000001", UserUpdate(language=SystemLocale.FI)
    )
    assert updated.language == SystemLocale.FI


@pytest.mark.asyncio
async def test_update_user_self_update_role_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-20: User cannot change their own role."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_selfrole00001",
        email="selfrole@test.com",
        name="Self Role",
        role=UserRole.MEMBER,
        organization_id="org_selfrole0001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(user)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_selfrole00001", "usr_selfrole00001", UserUpdate(role=UserRole.ADMIN)
        )
    assert "Users cannot change their own role." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_admin_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-21: Admin cannot update users in foreign org."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_adminup00001",
        email="adminup@test.com",
        name="Admin Up",
        role=UserRole.ADMIN,
        organization_id="org_admin_up0001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    target = User(
        id="usr_targetup0001",
        email="targetup@test.com",
        name="Target Up",
        role=UserRole.MEMBER,
        organization_id="org_target_up001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_adminup00001", "usr_targetup0001", UserUpdate(name="Hacked")
        )
    assert "Cannot update users from other organizations" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_non_root_transferring_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-22: Non-root user cannot transfer user to another org."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_adminxfer001",
        email="adminxfer@test.com",
        name="Admin Xfer",
        role=UserRole.ADMIN,
        organization_id="org_common_xfer",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    target = User(
        id="usr_targetxfer01",
        email="targetxfer@test.com",
        name="Target Xfer",
        role=UserRole.MEMBER,
        organization_id="org_common_xfer",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_adminxfer001", "usr_targetxfer01", UserUpdate(organization_id="org_new_xfer00001")
        )
    assert "Only ROOT can transfer users between organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_demoting_last_admin_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-23: Demoting last admin in org raises ConflictError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_rootdemote01",
        email="rootdemote@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    sole_admin = User(
        id="usr_soledm000001",
        email="sole@test.com",
        name="Sole Admin",
        role=UserRole.ADMIN,
        organization_id="org_sole_admin001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(sole_admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.update_user(
            "usr_rootdemote01", "usr_soledm000001", UserUpdate(role=UserRole.MEMBER)
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    assert exc_info.value.details["reason"] == "LAST_ADMIN_PROTECTION"


@pytest.mark.asyncio
async def test_update_user_role_root_initiator_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-24: ROOT updates role of user and emits audit event."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    root = User(
        id="usr_rootrole0001",
        email="rootrole@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    target = User(
        id="usr_targetrole01",
        email="targetrole@test.com",
        name="Target",
        role=UserRole.MEMBER,
        organization_id="org_role_test0001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(target)

    updated = await auth_service.update_user_role("usr_rootrole0001", "usr_targetrole01", UserRole.MANAGER)
    assert updated.role == UserRole.MANAGER
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "USER_ROLE_UPDATED"


@pytest.mark.asyncio
async def test_update_user_role_lower_hierarchy_modifying_higher_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-25: ADMIN modifying ROOT raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_adminmod0001",
        email="adminmod@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_mod0000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    root = User(
        id="usr_roottarget01",
        email="roottarget@test.com",
        name="Root Target",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(root)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role("usr_adminmod0001", "usr_roottarget01", UserRole.MEMBER)
    assert "Cannot modify users with higher or equal privileges." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_promoting_above_own_role_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-26: ADMIN promoting user to ROOT raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_adminpromo01",
        email="adminpromo@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_promo00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    member = User(
        id="usr_memberpromo1",
        email="memberpromo@test.com",
        name="Member",
        role=UserRole.MEMBER,
        organization_id="org_promo00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(member)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role("usr_adminpromo01", "usr_memberpromo1", UserRole.ROOT)
    assert "Cannot promote user to a role higher than your own." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_admin_modifying_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-27: Admin modifying user in another organization raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_adminfor0001",
        email="adminfor@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_one_role",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    target = User(
        id="usr_targetfor001",
        email="targetfor@test.com",
        name="Target",
        role=UserRole.MEMBER,
        organization_id="org_two_role",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role("usr_adminfor0001", "usr_targetfor001", UserRole.MANAGER)
    assert "Cannot manage users in other organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_demoting_last_admin_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-28: Demoting last admin in update_user_role raises ConflictError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_rootroledm01",
        email="rootdm@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    admin = User(
        id="usr_soledm000002",
        email="sole2@test.com",
        name="Sole Admin 2",
        role=UserRole.ADMIN,
        organization_id="org_sole_admin002",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.update_user_role("usr_rootroledm01", "usr_soledm000002", UserRole.MEMBER)
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    assert exc_info.value.details["reason"] == "LAST_ADMIN_PROTECTION"


@pytest.mark.asyncio
async def test_delete_user_root_initiator_regular_user_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-29: ROOT deletes user from repo and logs audit event."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    root = User(
        id="usr_rootdel00001",
        email="rootdel@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    user = User(
        id="usr_targetdel001",
        email="deltarget@test.com",
        name="Del Target",
        role=UserRole.MEMBER,
        organization_id="org_del0000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(user)

    result = await auth_service.delete_user("usr_rootdel00001", "usr_targetdel001")
    assert result is True
    assert await mock_repo.get_user("usr_targetdel001") is None
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "USER_DELETED"


@pytest.mark.asyncio
async def test_delete_user_admin_same_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-30: ADMIN deletes member in same org."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_admdel000001",
        email="admdel@test.com",
        name="Adm Del",
        role=UserRole.ADMIN,
        organization_id="org_del_same00001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    user = User(
        id="usr_delsame00001",
        email="delsame@test.com",
        name="Del Same",
        role=UserRole.MEMBER,
        organization_id="org_del_same00001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(user)

    result = await auth_service.delete_user("usr_admdel000001", "usr_delsame00001")
    assert result is True
    assert await mock_repo.get_user("usr_delsame00001") is None


@pytest.mark.asyncio
async def test_delete_user_admin_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-31: ADMIN deleting user in another org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_admdelfor001",
        email="admfor@test.com",
        name="Adm For",
        role=UserRole.ADMIN,
        organization_id="org_one_del",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    user = User(
        id="usr_delfor000001",
        email="delfor@test.com",
        name="Del For",
        role=UserRole.MEMBER,
        organization_id="org_two_del",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(user)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_user("usr_admdelfor001", "usr_delfor000001")
    assert "Cannot delete users from other organizations" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_user_root_account_protection_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-32: Deleting root master user raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@system.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_user(SYSTEM_ROOT_USER_ID, SYSTEM_ROOT_USER_ID)
    assert "The primary Root account cannot be deleted." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_user_last_admin_protection_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-33: Deleting last admin in an org raises ConflictError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_rootdeladm01",
        email="rootdeladm@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    sole_admin = User(
        id="usr_soledeladm01",
        email="soledeladm@test.com",
        name="Sole Admin Del",
        role=UserRole.ADMIN,
        organization_id="org_del_lastadm01",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(sole_admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.delete_user("usr_rootdeladm01", "usr_soledeladm01")
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    assert exc_info.value.details["reason"] == "LAST_ADMIN_PROTECTION"


@pytest.mark.asyncio
async def test_delete_user_not_found_raises_app_exception_404(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-34: Deleting non-existent user raises AppException 404."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_rootdelnotf1",
        email="rootnotf@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    with pytest.raises(AppException) as exc_info:
        await auth_service.delete_user("usr_rootdelnotf1", "usr_missingdel01")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_ensure_root_user_creates_system_org_if_missing(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-35: ensure_root_user creates system org if missing."""
    auth_service = AuthService(mock_repo)
    root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    retrieved_root = await auth_service.ensure_root_user()
    assert retrieved_root.id == SYSTEM_ROOT_USER_ID
    sys_org = await mock_repo.get_organization(SystemOrganizations.ROOT_SYSTEM)
    assert sys_org is not None
    assert sys_org.name == "System Administration"


@pytest.mark.asyncio
async def test_ensure_root_user_success_when_root_exists(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-36: ensure_root_user returns root user when already initialized."""
    auth_service = AuthService(mock_repo)
    sys_org = Organization(
        id=SystemOrganizations.ROOT_SYSTEM,
        name="System Administration",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(sys_org)
    root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    retrieved = await auth_service.ensure_root_user()
    assert retrieved.id == SYSTEM_ROOT_USER_ID


@pytest.mark.asyncio
async def test_ensure_root_user_heals_organization_id_if_drifted(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-37: ensure_root_user heals drifted organization_id to ROOT_SYSTEM."""
    auth_service = AuthService(mock_repo)
    sys_org = Organization(
        id=SystemOrganizations.ROOT_SYSTEM,
        name="System Administration",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(sys_org)
    drifted_root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id="org_drifted0000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(drifted_root)

    healed = await auth_service.ensure_root_user()
    assert healed.organization_id == SystemOrganizations.ROOT_SYSTEM


@pytest.mark.asyncio
async def test_ensure_root_user_missing_from_db_raises_app_exception_500(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-38: Missing root user from DB raises AppException 500 CONFIGURATION_ERROR."""
    auth_service = AuthService(mock_repo)

    with pytest.raises(AppException) as exc_info:
        await auth_service.ensure_root_user()
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_auth_service_facade_delegates_all_operations(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-39: AuthService facade delegates token, org, and user operations cleanly."""
    auth_service = AuthService(mock_repo)
    assert auth_service.token_service is not None
    assert auth_service.org_service is not None
    assert auth_service.user_service is not None

    # Test property setters synchronize across subservices
    auth_service.use_firebase = True
    assert auth_service.token_service.use_firebase is True
    assert auth_service.org_service.use_firebase is True
    assert auth_service.user_service.use_firebase is True

    mock_fb = MagicMock()
    auth_service.firebase_auth = mock_fb
    assert auth_service.token_service.firebase_auth is mock_fb
    assert auth_service.org_service.firebase_auth is mock_fb
    assert auth_service.user_service.firebase_auth is mock_fb

    auth_service._initialized_firebase = True
    assert auth_service.token_service._initialized_firebase is True


@pytest.mark.asyncio
async def test_direct_user_service_execution(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies direct instantiation and execution of UserService."""
    user_repo = UserRepository(mock_repo)
    org_repo = OrganizationRepository(mock_repo)
    mock_audit = AsyncMock()
    service = UserService(
        user_repo=user_repo,
        org_repo=org_repo,
        audit_service=mock_audit,
    )
    root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="rootdirect@example.com",
        name="Root Direct",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language="en",
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    ensured = await service.ensure_root_user()
    assert ensured.id == SYSTEM_ROOT_USER_ID

    created = await service.create_user(
        SYSTEM_ROOT_USER_ID,
        UserCreate(
            email="directuser@test.com",
            name="Direct User",
            role=UserRole.MEMBER,
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            is_active=True,
            language="en",
            theme_mode="system",
        ),
    )
    assert created.email == "directuser@test.com"

    root_token = TokenData(id=SYSTEM_ROOT_USER_ID, role=UserRole.ROOT)
    fetched = await service.get_user(root_token, created.id)
    assert fetched.id == created.id

    updated = await service.update_user(SYSTEM_ROOT_USER_ID, created.id, UserUpdate(name="Updated Direct"))
    assert updated.name == "Updated Direct"

    deleted = await service.delete_user(SYSTEM_ROOT_USER_ID, created.id)
    assert deleted is True




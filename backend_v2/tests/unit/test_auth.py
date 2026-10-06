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
    UserRepository,
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
async def test_auth_service_verify_token_mock_forbidden_in_production(mock_repo: InMemoryUnifiedWorkflowRepository, monkeypatch: Any) -> None:
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
    user = await get_my_profile(
        current_user=TokenData(id="usr_12345678", role=UserRole.MEMBER), auth_service=service
    )
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

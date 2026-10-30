"""Unit tests for user service."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Organization,
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
    LEGACY_ROOT_MASTER_ID,
    SYSTEM_ROOT_USER_ID,
    AuthService,
    OrganizationRepository,
    UserRepository,
    UserService,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


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
    mock_fb = MagicMock()
    auth = AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)

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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)

    payload = UserCreate(
        email="newadmin@test.com",
        name="New Admin",
        role=UserRole.ADMIN,
        organization_id="org_test00000001",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="member@test.com",
        name="Member User",
        role=UserRole.MEMBER,
        organization_id="org_test00000002",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="foreign@test.com",
        name="Foreign User",
        role=UserRole.MEMBER,
        organization_id="org_foreign00001",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="rootattempt@test.com",
        name="Root Attempt",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(manager)

    payload = UserCreate(
        email="sub@test.com",
        name="Subordinate",
        role=UserRole.MEMBER,
        organization_id="org_test00000005",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(member)

    payload = UserCreate(
        email="sub2@test.com",
        name="Sub2",
        role=UserRole.MEMBER,
        organization_id="org_test00000006",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="user_no_org@test.com",
        name="No Org",
        role=UserRole.MEMBER,
        organization_id="org_nonexistent01",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="badroot@test.com",
        name="Bad Root",
        role=UserRole.ROOT,
        organization_id="org_other0000001",
        is_active=True,
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user("usr_selfrole00001", "usr_selfrole00001", UserUpdate(role=UserRole.ADMIN))
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user("usr_adminup00001", "usr_targetup0001", UserUpdate(name="Hacked"))
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(sole_admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.update_user("usr_rootdemote01", "usr_soledm000001", UserUpdate(role=UserRole.MEMBER))
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
        language=SystemLocale.EN,
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
            language=SystemLocale.EN,
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


@pytest.mark.asyncio
async def test_user_service_firebase_delete_and_null_repo_returns(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test Firebase user deletion failure (Fail-Fast), force_org_id, and None repo return branches."""
    user_repo = UserRepository(mock_repo)
    org_repo = OrganizationRepository(mock_repo)
    mock_fb = MagicMock()
    service = UserService(
        user_repo=user_repo,
        org_repo=org_repo,
        use_firebase=True,
        firebase_auth=mock_fb,
    )

    org = Organization(
        id="org_fbdel00000001",
        name="FB Del Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)

    root = User(
        id="usr_rootfbdel0001",
        email="rootfb@test.com",
        name="Root FB",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    # 1. _create_user_internal with force_org_id
    forced_user = await service._create_user_internal(
        "usr_rootfbdel0001",
        UserCreate(
            email="forced@test.com",
            name="Forced Org User",
            role=UserRole.MEMBER,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        ),
        force_org_id="org_fbdel00000001",
    )
    assert forced_user.organization_id == "org_fbdel00000001"

    # 2. delete_user with Firebase error raises AppException 500
    mock_fb.delete_user.side_effect = RuntimeError("Firebase unavailable")
    with pytest.raises(AppException) as exc_fb_del:
        await service.delete_user("usr_rootfbdel0001", forced_user.id)
    assert exc_fb_del.value.status_code == 500
    assert exc_fb_del.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

    # 3. delete_user with Firebase success
    mock_fb.delete_user.side_effect = None
    assert await service.delete_user("usr_rootfbdel0001", forced_user.id) is True
    mock_fb.delete_user.assert_called_with(forced_user.id)

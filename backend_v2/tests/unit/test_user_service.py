"""Unit tests for user service."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

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
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import ExecutionStatus, SystemLocale
from backend_v2.services.auth import (
    SYSTEM_ROOT_USER_ID,
    AuthService,
    OrganizationRepository,
    UserRepository,
    UserService,
)
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> Iterator[InMemoryUnifiedWorkflowRepository]:
    """Provide an in-memory unified repository with deterministic fault cleanup."""
    repo = InMemoryUnifiedWorkflowRepository()
    try:
        yield repo
    finally:
        repo.clear_faults()


@pytest.mark.asyncio
async def test_auth_service_create_user_hierarchy_and_validations(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test create_user permissions, hierarchy constraints, and organization validations."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    creator_admin = User(
        id="usr_0195f3a0000070008000000000000001",
        email="creator@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000099",
    )
    mock_org = Organization(
        id="org_0195f3a0000070008000000000000099",
        name="My Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )

    # 1. Creator not found
    with pytest.raises(AppException) as exc_nf:
        await auth.create_user(
            "usr_0195f3a0000070008000000000000002",
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
            "usr_0195f3a0000070008000000000000001",
            UserCreate(
                email="u@test.com",
                role=UserRole.MEMBER,
                organization_id="org_0195f3a0000070008000000000000002",
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )

    # 3. Non-system org creating ROOT user
    with pytest.raises(PermissionDeniedError):
        await auth.create_user(
            "usr_0195f3a0000070008000000000000001",
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
            "usr_0195f3a0000070008000000000000001",
            UserCreate(
                email="u@test.com",
                role=UserRole.MEMBER,
                organization_id="org_0195f3a0000070008000000000000099",
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
        "usr_0195f3a0000070008000000000000001",
        UserCreate(
            email="member@test.com",
            role=UserRole.MEMBER,
            organization_id="org_0195f3a0000070008000000000000099",
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
        id="usr_0195f3a0000070008000000000000003",
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(UTC),
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
            created_at=datetime.now(UTC),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )

    # Firebase user created successfully
    mock_fb_user = MagicMock()
    mock_fb_user.id = "usr_0195f3a0000070008000000000000004"
    mock_fb.create_user.return_value = mock_fb_user

    created = await auth.create_user(
        "usr_0195f3a0000070008000000000000003",
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
    assert created.id == "usr_0195f3a0000070008000000000000004"

    # Firebase user exists fallback
    mock_fb.create_user.side_effect = RuntimeError("Email already exists")
    existing_fb = MagicMock()
    existing_fb.id = "usr_0195f3a0000070008000000000000005"
    mock_fb.get_user_by_email.return_value = existing_fb

    created_existing = await auth.create_user(
        "usr_0195f3a0000070008000000000000003",
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
    assert created_existing.id == "usr_0195f3a0000070008000000000000005"

    # Firebase creation completely fails
    mock_fb.get_user_by_email.side_effect = RuntimeError("Network error")
    with pytest.raises(AppException) as exc_fb:
        await auth.create_user(
            "usr_0195f3a0000070008000000000000003",
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
        id="usr_0195f3a0000070008000000000000006",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )
    target_member = User(
        id="usr_0195f3a0000070008000000000000007",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.delete_user("usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000007")
    assert exc_nf.value.status_code == 404

    # Seed initiator_admin and target_member
    await mock_repo.create_user(initiator_admin)
    await mock_repo.create_user(target_member)

    # 2. Admin cannot delete users from other organizations
    target_foreign = target_member.model_copy(
        update={"id": "usr_0195f3a0000070008000000000000008", "organization_id": "org_0195f3a0000070008000000000000004"}
    )
    await mock_repo.create_user(target_foreign)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000008")

    # 3. Member cannot delete users
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_0195f3a0000070008000000000000007", "usr_0195f3a0000070008000000000000007")

    # 4. Root accounts cannot be deleted
    root_acc1 = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=initiator_admin.organization_id,
    )
    root_acc2 = User.model_construct(
        id="usr_0195f3a00000700080000000000000ff",
        email="legacy_root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=initiator_admin.organization_id,
    )
    await mock_repo.create_user(root_acc1)
    await mock_repo.create_user(root_acc2)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_0195f3a0000070008000000000000006", SYSTEM_ROOT_USER_ID)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_user("usr_0195f3a0000070008000000000000006", SYSTEM_ROOT_USER_ID)

    # 5. Last Admin Protection: cannot delete last admin of org
    target_admin = initiator_admin.model_copy(update={"id": "usr_0195f3a0000070008000000000000009"})
    await mock_repo.create_user(target_admin)
    # Remove initiator_admin so target_admin is the ONLY admin in org_test00000001
    await mock_repo.delete_user("usr_0195f3a0000070008000000000000006")
    # Call with root user as initiator
    with pytest.raises(ConflictError) as exc_last_admin:
        await auth.delete_user(SYSTEM_ROOT_USER_ID, "usr_0195f3a0000070008000000000000009")
    assert exc_last_admin.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 6. Successful GDPR soft-delete with multiple admins and audit
    await mock_repo.create_user(initiator_admin)
    # Now there are 2 admins in org_test00000001 (initiator_admin and target_admin)
    deleted = await auth.delete_user("usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000007")
    assert deleted is True
    soft_deleted_user = await mock_repo.get_user("usr_0195f3a0000070008000000000000007")
    assert soft_deleted_user is not None
    assert soft_deleted_user.is_active is False
    assert soft_deleted_user.deleted_at is not None
    assert soft_deleted_user.email == "deleted_usr_0195f3a0000070008000000000000007@anonymized.quorum.local"
    assert soft_deleted_user.name == "Anonymized User"
    assert soft_deleted_user.firebase_uid is None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_update_user_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test update_user self-update, permissions, org transfer, last admin protection."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    admin_user = User(
        id="usr_0195f3a0000070008000000000000006",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )
    member_user = User(
        id="usr_0195f3a0000070008000000000000007",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.update_user(
            "usr_0195f3a0000070008000000000000002", "usr_0195f3a0000070008000000000000007", UserUpdate(name="Name")
        )
    assert exc_nf.value.status_code == 404

    # Seed admin_user and member_user
    await mock_repo.create_user(admin_user)
    await mock_repo.create_user(member_user)

    # 2. Self-update: cannot change own role
    with pytest.raises(PermissionDeniedError):
        await auth.update_user(
            "usr_0195f3a0000070008000000000000007",
            "usr_0195f3a0000070008000000000000007",
            UserUpdate(role=UserRole.ADMIN),
        )

    # 3. Cross-org admin update denied
    foreign_member = member_user.model_copy(
        update={"id": "usr_0195f3a0000070008000000000000008", "organization_id": "org_0195f3a0000070008000000000000004"}
    )
    await mock_repo.create_user(foreign_member)
    with pytest.raises(PermissionDeniedError):
        await auth.update_user(
            "usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000008", UserUpdate(name="New")
        )

    # 4. Member updating other user denied
    with pytest.raises(PermissionDeniedError):
        await auth.update_user(
            "usr_0195f3a0000070008000000000000007", "usr_0195f3a0000070008000000000000006", UserUpdate(name="New")
        )

    # 5. Non-root transferring user between orgs denied
    with pytest.raises(PermissionDeniedError):
        await auth.update_user(
            "usr_0195f3a0000070008000000000000006",
            "usr_0195f3a0000070008000000000000007",
            UserUpdate(organization_id="org_0195f3a0000070008000000000000005"),
        )

    # 6. Demoting last admin of an organization denied
    # admin_user is currently the only admin in org_test00000001
    root_user = admin_user.model_copy(update={"id": "usr_0195f3a000007000800000000000000a", "role": UserRole.ROOT})
    await mock_repo.create_user(root_user)
    with pytest.raises(ConflictError) as exc_demote:
        await auth.update_user(
            "usr_0195f3a000007000800000000000000a",
            "usr_0195f3a0000070008000000000000006",
            UserUpdate(role=UserRole.MEMBER),
        )
    assert exc_demote.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 7. Update fails on repository level raises 500
    mock_repo.inject_fault("update_user", AppException("Update failed", status_code=500), trigger_count=1)
    try:
        with pytest.raises(AppException) as exc_up_fail:
            await auth.update_user(
                "usr_0195f3a0000070008000000000000006",
                "usr_0195f3a0000070008000000000000007",
                UserUpdate(name="Failing"),
            )
        assert exc_up_fail.value.status_code == 500
    finally:
        mock_repo.clear_faults()

    # 8. Successful update with audit logging
    res = await auth.update_user(
        "usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000007", UserUpdate(name="Updated Name")
    )
    assert res.name == "Updated Name"
    updated_in_store = await mock_repo.get_user("usr_0195f3a0000070008000000000000007")
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
        id="usr_0195f3a0000070008000000000000006",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )
    manager_user = User(
        id="usr_0195f3a000007000800000000000000b",
        email="manager@test.com",
        role=UserRole.MANAGER,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )
    member_user = User(
        id="usr_0195f3a0000070008000000000000007",
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000003",
    )

    # 1. Initiator or target not found
    with pytest.raises(AppException) as exc_nf:
        await auth.update_user_role(
            "usr_0195f3a0000070008000000000000002", "usr_0195f3a0000070008000000000000007", UserRole.MANAGER
        )
    assert exc_nf.value.status_code == 404

    # Seed users
    await mock_repo.create_user(admin_user)
    await mock_repo.create_user(manager_user)
    await mock_repo.create_user(member_user)

    # 2. Lower role cannot modify higher privilege
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role(
            "usr_0195f3a0000070008000000000000007", "usr_0195f3a0000070008000000000000006", UserRole.MEMBER
        )

    # 3. Cannot promote to role higher than own
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role(
            "usr_0195f3a000007000800000000000000b", "usr_0195f3a0000070008000000000000007", UserRole.ADMIN
        )

    # 4. Admin managing user in other organization denied
    foreign_member = member_user.model_copy(
        update={"id": "usr_0195f3a000007000800000000000000c", "organization_id": "org_0195f3a0000070008000000000000004"}
    )
    await mock_repo.create_user(foreign_member)
    with pytest.raises(PermissionDeniedError):
        await auth.update_user_role(
            "usr_0195f3a0000070008000000000000006", "usr_0195f3a000007000800000000000000c", UserRole.MANAGER
        )

    # 5. Last admin demotion denied
    with pytest.raises(ConflictError) as exc_last_admin:
        await auth.update_user_role(
            "usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000006", UserRole.MEMBER
        )
    assert exc_last_admin.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 6. Update failure raises 500
    mock_repo.inject_fault("update_user", AppException("Update failed", status_code=500), trigger_count=1)
    try:
        with pytest.raises(AppException) as exc_fail:
            await auth.update_user_role(
                "usr_0195f3a0000070008000000000000006",
                "usr_0195f3a0000070008000000000000007",
                UserRole.MANAGER,
            )
        assert exc_fail.value.status_code == 500
    finally:
        mock_repo.clear_faults()

    # 7. Successful update
    res = await auth.update_user_role(
        "usr_0195f3a0000070008000000000000006", "usr_0195f3a0000070008000000000000007", UserRole.MANAGER
    )
    assert res.role == UserRole.MANAGER
    updated_in_store = await mock_repo.get_user("usr_0195f3a0000070008000000000000007")
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
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    root_user = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(UTC),
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
    drifted_root = root_user.model_copy(update={"organization_id": "org_0195f3a0000070008000000000000006"})
    await mock_repo.create_user(drifted_root)
    res_fixed = await auth.ensure_root_user()
    assert res_fixed.organization_id == SystemOrganizations.ROOT_SYSTEM
    refreshed = await mock_repo.get_user(SYSTEM_ROOT_USER_ID)
    assert refreshed is not None
    assert refreshed.organization_id == SystemOrganizations.ROOT_SYSTEM

    # Case 4: Root user refresh fails -> raises 500
    mock_repo.inject_fault("update_user", AppException("Update failure", status_code=500), trigger_count=1)
    try:
        await mock_repo.create_user(drifted_root)
        with pytest.raises(AppException) as exc_refresh_fail:
            await auth.ensure_root_user()
        assert exc_refresh_fail.value.status_code == 500
    finally:
        mock_repo.clear_faults()


@pytest.mark.asyncio
async def test_create_user_root_creator_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-01: ROOT creator can create an ADMIN user in any org with audit logging."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_0195f3a0000070008000000000000003",
        name="Test Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    root_user = User(
        id="usr_0195f3a000007000800000000000000a",
        email="root@test.com",
        name="Root User",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)

    payload = UserCreate(
        email="newadmin@test.com",
        name="New Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000003",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    created = await auth_service.create_user("usr_0195f3a000007000800000000000000a", payload)
    assert created.email == "newadmin@test.com"
    assert created.role == UserRole.ADMIN
    assert created.organization_id == "org_0195f3a0000070008000000000000003"
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "USER_CREATED"
    assert call_kwargs["actor_id"] == "usr_0195f3a000007000800000000000000a"


@pytest.mark.asyncio
async def test_create_user_admin_creator_same_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-02: ADMIN creator creates MEMBER in same org."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_0195f3a0000070008000000000000007",
        name="Test Org 2",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    admin_user = User(
        id="usr_0195f3a000007000800000000000000d",
        email="admin@test.com",
        name="Admin User",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000007",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="member@test.com",
        name="Member User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000007",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    created = await auth_service.create_user("usr_0195f3a000007000800000000000000d", payload)
    assert created.email == "member@test.com"
    assert created.role == UserRole.MEMBER


@pytest.mark.asyncio
async def test_create_user_admin_creator_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-03: ADMIN creating user targeting a foreign org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin_user = User(
        id="usr_0195f3a000007000800000000000000e",
        email="admin2@test.com",
        name="Admin 2",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000008",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    payload = UserCreate(
        email="foreign@test.com",
        name="Foreign User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000004",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_0195f3a000007000800000000000000e", payload)
    assert "Cannot create users in other organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_admin_creating_root_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-04: ADMIN attempting to create ROOT raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin_user = User(
        id="usr_0195f3a000007000800000000000000f",
        email="admin3@test.com",
        name="Admin 3",
        role=UserRole.ADMIN,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
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
        await auth_service.create_user("usr_0195f3a000007000800000000000000f", payload)
    assert "Admins cannot create Roots." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_manager_creating_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-05: MANAGER attempting to create user raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    await mock_repo.create_organization(
        Organization(
            id="org_0195f3a0000070008000000000000009",
            name="Org Test 5",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=1000.0,
            tpm_limit=10000,
            rpm_limit=100,
            allowed_email_domains=[],
        )
    )
    manager = User(
        id="usr_0195f3a0000070008000000000000010",
        email="mgr@test.com",
        name="Manager",
        role=UserRole.MANAGER,
        organization_id="org_0195f3a0000070008000000000000009",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(manager)

    payload = UserCreate(
        email="sub@test.com",
        name="Subordinate",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000009",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_0195f3a0000070008000000000000010", payload)
    assert "Managers are Technical Leads and cannot manage users. Ask an Admin." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_user_member_creating_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-06: MEMBER attempting to create user raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    await mock_repo.create_organization(
        Organization(
            id="org_0195f3a000007000800000000000000a",
            name="Org Test 6",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=1000.0,
            tpm_limit=10000,
            rpm_limit=100,
            allowed_email_domains=[],
        )
    )
    member = User(
        id="usr_0195f3a0000070008000000000000011",
        email="mem@test.com",
        name="Member",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000a",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(member)

    payload = UserCreate(
        email="sub2@test.com",
        name="Sub2",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000a",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_0195f3a0000070008000000000000011", payload)
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
        organization_id="org_0195f3a000007000800000000000000b",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(AppException) as exc_info:
        await auth_service.create_user("usr_0195f3a0000070008000000000000012", payload)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_create_user_non_existent_target_org_raises_app_exception_404(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-08: Non-existent target org raises AppException 404 VALIDATION_FAILED."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_0195f3a0000070008000000000000013",
        email="root2@test.com",
        name="Root 2",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="user_no_org@test.com",
        name="No Org",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000c",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(AppException) as exc_info:
        await auth_service.create_user("usr_0195f3a0000070008000000000000013", payload)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_create_user_root_role_in_non_system_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-09: Root role in non-system org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_0195f3a0000070008000000000000014",
        email="root3@test.com",
        name="Root 3",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    payload = UserCreate(
        email="badroot@test.com",
        name="Bad Root",
        role=UserRole.ROOT,
        organization_id="org_0195f3a0000070008000000000000005",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_user("usr_0195f3a0000070008000000000000014", payload)
    assert "Root users can only be created within the System Organization." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_root_initiator_any_user_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-10: ROOT initiator can get any user."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_0195f3a0000070008000000000000015",
        email="any@test.com",
        name="Any User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000d",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    root_token = TokenData(id="usr_0195f3a0000070008000000000000016", role=UserRole.ROOT)

    fetched = await auth_service.get_user(root_token, "usr_0195f3a0000070008000000000000015")
    assert fetched.id == "usr_0195f3a0000070008000000000000015"


@pytest.mark.asyncio
async def test_get_user_self_fetch_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-11: User can get themselves."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_0195f3a0000070008000000000000017",
        email="self@test.com",
        name="Self User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000e",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    self_token = TokenData(
        id="usr_0195f3a0000070008000000000000017",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000e",
    )

    fetched = await auth_service.get_user(self_token, "usr_0195f3a0000070008000000000000017")
    assert fetched.id == "usr_0195f3a0000070008000000000000017"


@pytest.mark.asyncio
async def test_get_user_admin_same_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-12: ADMIN can get user in same org."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_0195f3a0000070008000000000000018",
        email="same@test.com",
        name="Same Org User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000000f",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    admin_token = TokenData(
        id="usr_0195f3a0000070008000000000000019",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a000007000800000000000000f",
    )

    fetched = await auth_service.get_user(admin_token, "usr_0195f3a0000070008000000000000018")
    assert fetched.id == "usr_0195f3a0000070008000000000000018"


@pytest.mark.asyncio
async def test_get_user_foreign_user_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-13: Fetching user from foreign org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_0195f3a000007000800000000000001a",
        email="foreign@test.com",
        name="Foreign User",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000010",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    initiator_token = TokenData(
        id="usr_0195f3a000007000800000000000001b",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000011",
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.get_user(initiator_token, "usr_0195f3a000007000800000000000001a")
    assert "You do not have permission to view this user." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_user_not_found_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-14: Fetching non-existent user raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_token = TokenData(id="usr_0195f3a0000070008000000000000016", role=UserRole.ROOT)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.get_user(root_token, "usr_0195f3a000007000800000000000001c")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_type"] == "user"
    assert exc_info.value.details["resource_id"] == "usr_0195f3a000007000800000000000001c"


@pytest.mark.asyncio
async def test_list_users_root_initiator_returns_all_users(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-15: ROOT initiator lists all users across organizations."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_0195f3a000007000800000000000001d",
        email="u1@test.com",
        name="U1",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000012",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    u2 = User(
        id="usr_0195f3a000007000800000000000001e",
        email="u2@test.com",
        name="U2",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000013",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)
    root_token = TokenData(id="usr_0195f3a0000070008000000000000016", role=UserRole.ROOT)

    users = await auth_service.list_users(root_token)
    assert len(users) == 2
    assert {u.id for u in users} == {"usr_0195f3a000007000800000000000001d", "usr_0195f3a000007000800000000000001e"}


@pytest.mark.asyncio
async def test_list_users_tenant_initiator_returns_own_org_users_only(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-16: Tenant initiator lists only users in their own org."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_0195f3a000007000800000000000001f",
        email="t1@test.com",
        name="T1",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000014",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    u2 = User(
        id="usr_0195f3a0000070008000000000000020",
        email="t2@test.com",
        name="T2",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000015",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)
    initiator = TokenData(
        id="usr_0195f3a000007000800000000000001f",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000014",
    )

    users = await auth_service.list_users(initiator)
    assert len(users) == 1
    assert users[0].id == "usr_0195f3a000007000800000000000001f"


@pytest.mark.asyncio
async def test_get_users_by_organization_returns_matching_users(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-17: get_users_by_organization retrieves matching users."""
    auth_service = AuthService(mock_repo)
    u1 = User(
        id="usr_0195f3a0000070008000000000000021",
        email="bo1@test.com",
        name="BO1",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000016",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(u1)

    matching = await auth_service.get_users_by_organization("org_0195f3a0000070008000000000000016")
    assert len(matching) == 1
    assert matching[0].id == "usr_0195f3a0000070008000000000000021"


@pytest.mark.asyncio
async def test_update_user_root_initiator_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-18: ROOT initiator updates user and emits audit event."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    user = User(
        id="usr_0195f3a0000070008000000000000022",
        email="up@test.com",
        name="Old Name",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000017",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    root = User(
        id="usr_0195f3a0000070008000000000000023",
        email="root4@test.com",
        name="Root 4",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    await mock_repo.create_user(root)

    updated = await auth_service.update_user(
        "usr_0195f3a0000070008000000000000023", "usr_0195f3a0000070008000000000000022", UserUpdate(name="New Name")
    )
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
        id="usr_0195f3a0000070008000000000000024",
        email="selfup@test.com",
        name="Self Up",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000018",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)

    updated = await auth_service.update_user(
        "usr_0195f3a0000070008000000000000024",
        "usr_0195f3a0000070008000000000000024",
        UserUpdate(language=SystemLocale.FI),
    )
    assert updated.language == SystemLocale.FI


@pytest.mark.asyncio
async def test_update_user_self_update_role_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-20: User cannot change their own role."""
    auth_service = AuthService(mock_repo)
    user = User(
        id="usr_0195f3a0000070008000000000000025",
        email="selfrole@test.com",
        name="Self Role",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000019",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_0195f3a0000070008000000000000025",
            "usr_0195f3a0000070008000000000000025",
            UserUpdate(role=UserRole.ADMIN),
        )
    assert "Users cannot change their own role." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_admin_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-21: Admin cannot update users in foreign org."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_0195f3a0000070008000000000000026",
        email="adminup@test.com",
        name="Admin Up",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a000007000800000000000001a",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    target = User(
        id="usr_0195f3a0000070008000000000000027",
        email="targetup@test.com",
        name="Target Up",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000001b",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_0195f3a0000070008000000000000026", "usr_0195f3a0000070008000000000000027", UserUpdate(name="Hacked")
        )
    assert "Cannot update users from other organizations" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_non_root_transferring_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-22: Non-root user cannot transfer user to another org."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_0195f3a0000070008000000000000028",
        email="adminxfer@test.com",
        name="Admin Xfer",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a000007000800000000000001c",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    target = User(
        id="usr_0195f3a0000070008000000000000029",
        email="targetxfer@test.com",
        name="Target Xfer",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000001c",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user(
            "usr_0195f3a0000070008000000000000028",
            "usr_0195f3a0000070008000000000000029",
            UserUpdate(organization_id="org_0195f3a000007000800000000000001d"),
        )
    assert "Only ROOT can transfer users between organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_demoting_last_admin_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-23: Demoting last admin in org raises ConflictError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_0195f3a000007000800000000000002a",
        email="rootdemote@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    sole_admin = User(
        id="usr_0195f3a000007000800000000000002b",
        email="sole@test.com",
        name="Sole Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a000007000800000000000001e",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(sole_admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.update_user(
            "usr_0195f3a000007000800000000000002a",
            "usr_0195f3a000007000800000000000002b",
            UserUpdate(role=UserRole.MEMBER),
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
        id="usr_0195f3a000007000800000000000002c",
        email="rootrole@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    target = User(
        id="usr_0195f3a000007000800000000000002d",
        email="targetrole@test.com",
        name="Target",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a000007000800000000000001f",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(target)

    updated = await auth_service.update_user_role(
        "usr_0195f3a000007000800000000000002c", "usr_0195f3a000007000800000000000002d", UserRole.MANAGER
    )
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
        id="usr_0195f3a000007000800000000000002e",
        email="adminmod@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000020",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    root = User(
        id="usr_0195f3a000007000800000000000002f",
        email="roottarget@test.com",
        name="Root Target",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(root)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role(
            "usr_0195f3a000007000800000000000002e", "usr_0195f3a000007000800000000000002f", UserRole.MEMBER
        )
    assert "Cannot modify users with higher or equal privileges." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_promoting_above_own_role_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-26: ADMIN promoting user to ROOT raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_0195f3a0000070008000000000000030",
        email="adminpromo@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000021",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    member = User(
        id="usr_0195f3a0000070008000000000000031",
        email="memberpromo@test.com",
        name="Member",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000021",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(member)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role(
            "usr_0195f3a0000070008000000000000030", "usr_0195f3a0000070008000000000000031", UserRole.ROOT
        )
    assert "Cannot promote user to a role higher than your own." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_admin_modifying_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-27: Admin modifying user in another organization raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_0195f3a0000070008000000000000032",
        email="adminfor@test.com",
        name="Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000022",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    target = User(
        id="usr_0195f3a0000070008000000000000033",
        email="targetfor@test.com",
        name="Target",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000023",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(target)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_user_role(
            "usr_0195f3a0000070008000000000000032", "usr_0195f3a0000070008000000000000033", UserRole.MANAGER
        )
    assert "Cannot manage users in other organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_role_demoting_last_admin_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-28: Demoting last admin in update_user_role raises ConflictError."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_0195f3a0000070008000000000000034",
        email="rootdm@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    admin = User(
        id="usr_0195f3a0000070008000000000000035",
        email="sole2@test.com",
        name="Sole Admin 2",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000024",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.update_user_role(
            "usr_0195f3a0000070008000000000000034", "usr_0195f3a0000070008000000000000035", UserRole.MEMBER
        )
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
        id="usr_0195f3a0000070008000000000000036",
        email="rootdel@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user = User(
        id="usr_0195f3a0000070008000000000000037",
        email="deltarget@test.com",
        name="Del Target",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000025",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(user)

    result = await auth_service.delete_user(
        "usr_0195f3a0000070008000000000000036", "usr_0195f3a0000070008000000000000037"
    )
    assert result is True
    soft_deleted = await mock_repo.get_user("usr_0195f3a0000070008000000000000037")
    assert soft_deleted is not None
    assert soft_deleted.is_active is False
    assert soft_deleted.deleted_at is not None
    assert soft_deleted.email == "deleted_usr_0195f3a0000070008000000000000037@anonymized.quorum.local"
    assert soft_deleted.name == "Anonymized User"
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
        id="usr_0195f3a0000070008000000000000038",
        email="admdel@test.com",
        name="Adm Del",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000026",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user = User(
        id="usr_0195f3a0000070008000000000000039",
        email="delsame@test.com",
        name="Del Same",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000026",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(user)

    result = await auth_service.delete_user(
        "usr_0195f3a0000070008000000000000038", "usr_0195f3a0000070008000000000000039"
    )
    assert result is True
    soft_deleted = await mock_repo.get_user("usr_0195f3a0000070008000000000000039")
    assert soft_deleted is not None
    assert soft_deleted.is_active is False
    assert soft_deleted.deleted_at is not None
    assert soft_deleted.email == "deleted_usr_0195f3a0000070008000000000000039@anonymized.quorum.local"
    assert soft_deleted.name == "Anonymized User"


@pytest.mark.asyncio
async def test_delete_user_admin_foreign_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-31: ADMIN deleting user in another org raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    admin = User(
        id="usr_0195f3a000007000800000000000003a",
        email="admfor@test.com",
        name="Adm For",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000027",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user = User(
        id="usr_0195f3a000007000800000000000003b",
        email="delfor@test.com",
        name="Del For",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000028",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin)
    await mock_repo.create_user(user)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_user("usr_0195f3a000007000800000000000003a", "usr_0195f3a000007000800000000000003b")
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
        created_at=datetime.now(UTC),
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
        id="usr_0195f3a000007000800000000000003c",
        email="rootdeladm@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    sole_admin = User(
        id="usr_0195f3a000007000800000000000003d",
        email="soledeladm@test.com",
        name="Sole Admin Del",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000029",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)
    await mock_repo.create_user(sole_admin)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.delete_user("usr_0195f3a000007000800000000000003c", "usr_0195f3a000007000800000000000003d")
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    assert exc_info.value.details["reason"] == "LAST_ADMIN_PROTECTION"


@pytest.mark.asyncio
async def test_delete_user_not_found_raises_app_exception_404(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-34: Deleting non-existent user raises AppException 404."""
    auth_service = AuthService(mock_repo)
    root = User(
        id="usr_0195f3a000007000800000000000003e",
        email="rootnotf@test.com",
        name="Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    with pytest.raises(AppException) as exc_info:
        await auth_service.delete_user("usr_0195f3a000007000800000000000003e", "usr_0195f3a000007000800000000000003f")
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(sys_org)
    root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(sys_org)
    drifted_root = User(
        id=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        name="Root Master",
        role=UserRole.ROOT,
        organization_id="org_0195f3a000007000800000000000002a",
        is_active=True,
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        id="org_0195f3a000007000800000000000002b",
        name="FB Del Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)

    root = User(
        id="usr_0195f3a0000070008000000000000040",
        email="rootfb@test.com",
        name="Root FB",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root)

    # 1. _create_user_internal with force_org_id
    forced_user = await service._create_user_internal(
        "usr_0195f3a0000070008000000000000040",
        UserCreate(
            email="forced@test.com",
            name="Forced Org User",
            role=UserRole.MEMBER,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        ),
        force_org_id="org_0195f3a000007000800000000000002b",
    )
    assert forced_user.organization_id == "org_0195f3a000007000800000000000002b"

    # 2. delete_user with Firebase error raises AppException 500
    mock_fb.delete_user.side_effect = RuntimeError("Firebase unavailable")
    with pytest.raises(AppException) as exc_fb_del:
        await service.delete_user("usr_0195f3a0000070008000000000000040", forced_user.id)
    assert exc_fb_del.value.status_code == 500
    assert exc_fb_del.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

    # 3. delete_user with Firebase success
    mock_fb.delete_user.side_effect = None
    assert await service.delete_user("usr_0195f3a0000070008000000000000040", forced_user.id) is True
    mock_fb.delete_user.assert_called_with(forced_user.id)


@pytest.mark.asyncio
async def test_user_service_with_exchanged_quorum_jwt_token_data(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify UserService accepts stateless TokenData decoded from an exchanged Quorum Local JWT."""
    from pydantic import SecretStr

    from backend_v2.models.auth import TokenExchangeRequestDTO
    from backend_v2.settings import Settings

    cli_secret = SecretStr("test_user_service_cli_secret_2026")
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
        service_auth_secret=cli_secret,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)

    admin_user = User(
        id="usr_0195f3a0000070008000000000000091",
        email="jwt_admin@test.com",
        name="JWT Admin",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000091",
        is_active=True,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(admin_user)

    auth_service = AuthService(mock_repo, use_firebase=False)
    exchanged = await auth_service.token_service.exchange_firebase_token(
        TokenExchangeRequestDTO(target_user_id=admin_user.id, service_auth_secret=cli_secret)
    )
    verified_token_data = await auth_service.verify_token(exchanged.access_token)
    assert verified_token_data.mfa_verified is True
    assert verified_token_data.jti is not None

    users = await auth_service.list_users(verified_token_data)
    assert len(users) == 1
    assert users[0].id == admin_user.id


@pytest.mark.asyncio
async def test_user_service_self_update_hierarchy_last_admin_and_revocation(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify self-update guards, role hierarchy, soft-delete aware LAST_ADMIN_PROTECTION, and RevocationCache."""
    mock_revocation = MagicMock(revoke_user_sessions=AsyncMock())
    auth_service = AuthService(mock_repo, use_firebase=False, revocation_cache=mock_revocation)

    org_id = "org_0195f3a00000700080000000000000c1"
    root_id = "usr_0195f3a00000700080000000000000c0"
    admin_id = "usr_0195f3a00000700080000000000000c1"
    deleted_admin_id = "usr_0195f3a00000700080000000000000c2"
    manager_id = "usr_0195f3a00000700080000000000000c3"
    member_id = "usr_0195f3a00000700080000000000000c4"

    await mock_repo.create_user(
        User(
            id=root_id,
            email="root52@test.com",
            name="Root",
            role=UserRole.ROOT,
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=admin_id,
            email="admin52@test.com",
            name="Active Admin",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=deleted_admin_id,
            email="deleted_admin52@test.com",
            name="Deleted Admin",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            deleted_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=manager_id,
            email="mgr52@test.com",
            name="Manager",
            role=UserRole.MANAGER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=member_id,
            email="mem52@test.com",
            name="Member",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )

    # 1. Self-update blocked fields (organization_id, is_active, password)
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_user(
            member_id, member_id, UserUpdate(organization_id="org_0195f3a00000700080000000000000ff")
        )
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_user(member_id, member_id, UserUpdate(is_active=False))
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_user(member_id, member_id, UserUpdate(password="newpass123"))

    # 2. MANAGER can view org user via get_user, but MEMBER cannot view peer user in same org
    mgr_tok = TokenData(id=manager_id, role=UserRole.MANAGER, organization_id=org_id)
    mem_tok = TokenData(id=member_id, role=UserRole.MEMBER, organization_id=org_id)
    assert (await auth_service.get_user(mgr_tok, member_id)).id == member_id
    with pytest.raises(PermissionDeniedError):
        await auth_service.get_user(mem_tok, manager_id)

    # 3. Soft-delete aware LAST_ADMIN_PROTECTION on deactivating the sole non-deleted ADMIN
    with pytest.raises(ConflictError) as deact_exc:
        await auth_service.update_user(root_id, admin_id, UserUpdate(is_active=False))
    assert deact_exc.value.details["reason"] == "LAST_ADMIN_PROTECTION"

    # 4. ADMIN modifying higher role in update_user raises PermissionDeniedError
    await mock_repo.create_user(
        User(
            id="usr_0195f3a00000700080000000000000c5",
            email="root_in_org@test.com",
            name="Root In Org",
            role=UserRole.ROOT,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_user(
            admin_id, "usr_0195f3a00000700080000000000000c5", UserUpdate(role=UserRole.MEMBER)
        )

    # 5. RevocationCache triggered on update_user (is_active=False) and update_user_role
    await auth_service.update_user(admin_id, member_id, UserUpdate(is_active=False))
    mock_revocation.revoke_user_sessions.assert_awaited_with(member_id, ttl_seconds=900)

    mock_revocation.revoke_user_sessions.reset_mock()
    await auth_service.update_user_role(admin_id, member_id, UserRole.VIEWER)
    mock_revocation.revoke_user_sessions.assert_awaited_with(member_id, ttl_seconds=900)


@pytest.mark.asyncio
async def test_gdpr_soft_delete_preserves_executions_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract test_gdpr_soft_delete_preserves_executions_positive: soft-delete revokes sessions, anonymizes user, and preserves executions."""
    import hashlib
    import hmac

    from pydantic import SecretStr

    from backend_v2.settings import Settings

    webhook_secret = "whsec_gdpr_soft_delete_test_secret_2026"
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        firebase_webhook_secret=SecretStr(webhook_secret),
    )
    monkeypatch.setattr("backend_v2.services.auth.user_service.get_settings", lambda: mock_settings)

    mock_revocation = MagicMock(revoke_user_sessions=AsyncMock())
    mock_audit = MagicMock(log_event=AsyncMock())
    auth_service = AuthService(
        mock_repo,
        use_firebase=False,
        audit_service=mock_audit,
        revocation_cache=mock_revocation,
    )

    org_id = "org_0195f3a00000700080000000000000d1"
    admin_id = "usr_0195f3a00000700080000000000000d1"
    user1_id = "usr_0195f3a00000700080000000000000d2"
    user2_id = "usr_0195f3a00000700080000000000000d3"

    await mock_repo.create_user(
        User(
            id=admin_id,
            email="admin_gdpr@test.com",
            name="Admin GDPR",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=user1_id,
            email="member_gdpr1@test.com",
            name="Member GDPR One",
            firebase_uid="fb_uid_gdpr_1",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=user2_id,
            email="member_gdpr2@test.com",
            name="Member GDPR Two",
            firebase_uid="fb_uid_gdpr_2",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )

    exec1 = ExecutionRecordFactory.build(
        id="exe_0195f3a00000700080000000000000d1",
        workflow_id="wor_0195f3a0000070008000000000000001",
        status=ExecutionStatus.PENDING,
        created_at=datetime.now(UTC),
        created_by=user1_id,
        organization_id=org_id,
        target_locale=SystemLocale.EN,
    )
    exec2 = ExecutionRecordFactory.build(
        id="exe_0195f3a00000700080000000000000d2",
        workflow_id="wor_0195f3a0000070008000000000000001",
        status=ExecutionStatus.PENDING,
        created_at=datetime.now(UTC),
        created_by=user2_id,
        organization_id=org_id,
        target_locale=SystemLocale.EN,
    )
    await mock_repo.save_execution(exec1)
    await mock_repo.save_execution(exec2)

    # 1. Direct UserService.delete_user soft-deletes user1 and preserves exec1 foreign key
    assert await auth_service.delete_user(admin_id, user1_id) is True
    mock_revocation.revoke_user_sessions.assert_awaited_with(user1_id, ttl_seconds=900)
    anon1 = await mock_repo.get_user(user1_id)
    assert anon1 is not None
    assert anon1.is_active is False
    assert anon1.deleted_at is not None
    assert anon1.email == f"deleted_{user1_id}@anonymized.quorum.local"
    assert anon1.name == "Anonymized User"
    assert anon1.firebase_uid is None
    saved_exec1 = await mock_repo.get_execution(exec1.id)
    assert saved_exec1 is not None
    assert saved_exec1.created_by == user1_id

    # 2. Firebase deletion webhook soft-deletes user2 by firebase_uid and preserves exec2 foreign key
    mock_revocation.revoke_user_sessions.reset_mock()
    sig = hmac.new(webhook_secret.encode("utf-8"), b"fb_uid_gdpr_2", hashlib.sha256).hexdigest()
    webhook_res = await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
        firebase_uid="fb_uid_gdpr_2",
        signature_header=f"sha256={sig}",
        raw_body=b"",
    )
    assert webhook_res.status == "success"
    assert webhook_res.id == "fb_uid_gdpr_2"
    mock_revocation.revoke_user_sessions.assert_awaited_with(user2_id, ttl_seconds=900)
    anon2 = await mock_repo.get_user(user2_id)
    assert anon2 is not None
    assert anon2.is_active is False
    assert anon2.deleted_at is not None
    assert anon2.email == f"deleted_{user2_id}@anonymized.quorum.local"
    assert anon2.name == "Anonymized User"
    assert anon2.firebase_uid is None
    saved_exec2 = await mock_repo.get_execution(exec2.id)
    assert saved_exec2 is not None
    assert saved_exec2.created_by == user2_id


@pytest.mark.asyncio
async def test_gdpr_soft_delete_webhook_negative_and_boundary(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative & Boundary: Verify webhook HMAC validation failures, missing secret, root protection, and last admin protection."""
    import hashlib
    import hmac

    from pydantic import SecretStr

    from backend_v2.settings import Settings

    auth_service = AuthService(mock_repo, use_firebase=False)

    # 1. Missing firebase_webhook_secret raises CONFIGURATION_ERROR
    no_secret_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        firebase_webhook_secret=None,
    )
    monkeypatch.setattr("backend_v2.services.auth.user_service.get_settings", lambda: no_secret_settings)
    with pytest.raises(AppException) as no_sec_exc:
        await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
            firebase_uid="fb_any",
            signature_header="sha256=deadbeef",
        )
    assert no_sec_exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    # 2. Missing or invalid HMAC signature raises AuthenticationError
    secret_str = "whsec_boundary_test_2026"
    valid_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        firebase_webhook_secret=SecretStr(secret_str),
    )
    monkeypatch.setattr("backend_v2.services.auth.user_service.get_settings", lambda: valid_settings)

    with pytest.raises(AuthenticationError) as missing_sig_exc:
        await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
            firebase_uid="fb_any",
            signature_header="   ",
        )
    assert missing_sig_exc.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    with pytest.raises(AuthenticationError) as bad_sig_exc:
        await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
            firebase_uid="fb_any",
            signature_header="invalid_hmac_digest",
            raw_body=b'{"uid":"fb_any"}',
        )
    assert bad_sig_exc.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # 3. Valid body HMAC signature but missing user raises ResourceNotFoundError
    body_bytes = b'{"uid":"fb_missing_user"}'
    body_sig = hmac.new(secret_str.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    with pytest.raises(ResourceNotFoundError):
        await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
            firebase_uid="fb_missing_user",
            signature_header=body_sig,
            raw_body=body_bytes,
        )

    # 4. Root account protection and Last Admin protection on soft_delete_by_firebase_uid
    await mock_repo.create_user(
        User(
            id=SYSTEM_ROOT_USER_ID,
            email="root_wh@test.com",
            name="Root WH",
            firebase_uid="fb_root_master",
            role=UserRole.ROOT,
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    with pytest.raises(PermissionDeniedError):
        await auth_service.user_service.soft_delete_by_firebase_uid("fb_root_master")

    sole_admin_id = "usr_0195f3a00000700080000000000000e9"
    await mock_repo.create_user(
        User(
            id=sole_admin_id,
            email="sole_adm_wh@test.com",
            name="Sole Admin WH",
            firebase_uid="fb_sole_admin_wh",
            role=UserRole.ADMIN,
            organization_id="org_0195f3a00000700080000000000000e9",
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    with pytest.raises(ConflictError) as last_adm_exc:
        await auth_service.user_service.soft_delete_by_firebase_uid("fb_sole_admin_wh")
    assert last_adm_exc.value.details["reason"] == "LAST_ADMIN_PROTECTION"


@pytest.mark.asyncio
async def test_user_service_firebase_timeout_and_role_boundary_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative & Boundary: Verify bounded Firebase I/O timeouts, MANAGER role-update denial, and null update guards."""
    from backend_v2.settings import Settings

    short_timeout_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        http_client_timeout_seconds=0.1,
    )
    monkeypatch.setattr("backend_v2.services.auth.user_service.get_settings", lambda: short_timeout_settings)

    def _blocking_fb_op(*_args: object, **_kwargs: object) -> object:
        threading.Event().wait(0.35)
        mock_fb_res = MagicMock()
        mock_fb_res.id = "usr_0195f3a00000700080000000000000fa"
        return mock_fb_res

    mock_fb = MagicMock()
    mock_fb.create_user.side_effect = _blocking_fb_op
    mock_fb.get_user_by_email.side_effect = _blocking_fb_op
    mock_fb.delete_user.side_effect = _blocking_fb_op

    user_repo = UserRepository(mock_repo)
    org_repo = OrganizationRepository(mock_repo)
    service = UserService(
        user_repo=user_repo,
        org_repo=org_repo,
        use_firebase=True,
        firebase_auth=mock_fb,
    )

    org_id = "org_0195f3a00000700080000000000000f1"
    root_id = SYSTEM_ROOT_USER_ID
    admin_id = "usr_0195f3a00000700080000000000000f1"
    inactive_admin_id = "usr_0195f3a00000700080000000000000f2"
    manager_id = "usr_0195f3a00000700080000000000000f3"
    member_id = "usr_0195f3a00000700080000000000000f4"

    await mock_repo.create_organization(
        Organization(
            id=org_id,
            name="Boundary Org",
            is_active=True,
            created_at=datetime.now(UTC),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )
    await mock_repo.create_user(
        User(
            id=root_id,
            email="root_bound@test.com",
            name="Root Bound",
            role=UserRole.ROOT,
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=admin_id,
            email="admin_bound@test.com",
            name="Admin Bound",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=inactive_admin_id,
            email="inactive_admin@test.com",
            name="Inactive Admin",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=False,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=manager_id,
            email="mgr_bound@test.com",
            name="Manager Bound",
            role=UserRole.MANAGER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.create_user(
        User(
            id=member_id,
            email="mem_bound@test.com",
            name="Member Bound",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )

    # 1. Bounded Firebase create_user timeout raises AppException 500 INTERNAL_SERVER_ERROR
    with pytest.raises(AppException) as create_timeout_exc:
        await service.create_user(
            root_id,
            UserCreate(
                email="timeout_create@test.com",
                password="password123",
                name="Timeout User",
                role=UserRole.MEMBER,
                organization_id=org_id,
                is_active=True,
                language=SystemLocale.EN,
                theme_mode="system",
            ),
        )
    assert create_timeout_exc.value.status_code == 500
    assert create_timeout_exc.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

    # 2. Bounded Firebase delete_user timeout raises AppException 500 INTERNAL_SERVER_ERROR
    with pytest.raises(AppException) as delete_timeout_exc:
        await service.delete_user(root_id, member_id)
    assert delete_timeout_exc.value.status_code == 500
    assert delete_timeout_exc.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

    # 3. MANAGER attempting update_user_role on lower-ranked MEMBER raises PermissionDeniedError
    with pytest.raises(PermissionDeniedError) as mgr_role_exc:
        await service.update_user_role(manager_id, member_id, UserRole.VIEWER)
    assert "Insufficient permissions to update user roles." in str(mgr_role_exc.value)

    # 4. Boundary: updating inactive admin role or active admin name does not trigger LAST_ADMIN_PROTECTION
    demoted_inactive = await service.update_user(root_id, inactive_admin_id, UserUpdate(role=UserRole.MEMBER))
    assert demoted_inactive.role == UserRole.MEMBER
    renamed_sole_admin = await service.update_user(root_id, admin_id, UserUpdate(name="Renamed Sole Admin"))
    assert renamed_sole_admin.name == "Renamed Sole Admin"

    # 5. Concurrent vanishing record returning None from UserRepository.update raises AppException 500
    with pytest.raises(AppException) as null_update_exc:
        await service._apply_user_update_or_raise(
            "usr_0195f3a00000700080000000000000ff",
            UserUpdate(name="Lost"),
            failure_message="User update failed (not found despite check).",
        )
    assert null_update_exc.value.status_code == 500
    assert null_update_exc.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value

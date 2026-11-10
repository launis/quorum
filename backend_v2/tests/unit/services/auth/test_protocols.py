"""Unit tests for UserCreatorProtocol bounded context decoupling in auth services."""

from __future__ import annotations

import re
from datetime import UTC, datetime

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
)
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, generate_opaque_id
from backend_v2.models.enums import EntityPrefix, SystemLocale
from backend_v2.services.auth import OrganizationRepository, OrganizationService, UserRepository, UserService
from backend_v2.services.auth.protocols import UserCreatorProtocol
from backend_v2.services.auth.protocols import __all__ as protocols_all
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

__all__ = [
    "test_organization_service_missing_user_creator_protocol_raises_configuration_error",
    "test_user_creator_protocol_boundary_and_structural_rejection",
    "test_user_creator_protocol_cross_tenant_violation_raises_permission_denied",
    "test_user_creator_protocol_structural_conformance_and_org_provisioning",
    "test_user_creator_protocol_unknown_creator_raises_resource_not_found",
]

_OPAQUE_ID_PATTERN: re.Pattern[str] = re.compile(OPAQUE_STRIPE_ID_REGEX)


class _OrganizationModelFactory(ModelFactory[Organization]):
    """Hermetic Polyfactory builder for Organization domain models."""

    __model__ = Organization
    __set_as_default_factory_for_type__ = False

    name: str = "Acme Enterprise"
    is_active: bool = True
    tier: str = "enterprise"
    subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    quota_limit: float = 500.0
    tpm_limit: int = 50000
    rpm_limit: int = 500
    slug: str | None = None
    contact_email: str | None = None
    billing_id: str | None = None

    @classmethod
    def allowed_email_domains(cls) -> list[str]:
        """Generate an empty allowed email domains list.

        Returns:
            Empty list of allowed email domains.
        """
        return []

    @classmethod
    def id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 organization identifier.

        Returns:
            Canonical Organization Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def created_at(cls) -> datetime:
        """Generate a UTC creation timestamp.

        Returns:
            Timezone-aware UTC datetime.
        """
        return datetime.now(UTC)


class _OrganizationCreateFactory(ModelFactory[OrganizationCreate]):
    """Hermetic Polyfactory builder for OrganizationCreate payloads."""

    __model__ = OrganizationCreate
    __set_as_default_factory_for_type__ = False

    name: str = "Nordic Analytics Oy"
    admin_email: str = "admin@nordic.example.com"
    admin_password: str = "secret123"
    admin_name: str = "Nordic Admin"
    tpm_limit: int = 50000
    rpm_limit: int = 500


class _UserModelFactory(ModelFactory[User]):
    """Hermetic Polyfactory builder for User domain models."""

    __model__ = User
    __set_as_default_factory_for_type__ = False

    email: str = "root@quorum.example.com"
    name: str | None = "Platform Root"
    role: UserRole = UserRole.ROOT
    is_active: bool = True
    language: SystemLocale = SystemLocale.EN
    theme_mode: str = "system"
    slug: str | None = None
    created_by: str | None = None
    firebase_uid: str | None = None
    deleted_at: datetime | None = None

    @classmethod
    def id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 user identifier.

        Returns:
            Canonical User Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 organization identifier.

        Returns:
            Canonical Organization Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def created_at(cls) -> datetime:
        """Generate a UTC creation timestamp.

        Returns:
            Timezone-aware UTC datetime.
        """
        return datetime.now(UTC)


class _UserCreateFactory(ModelFactory[UserCreate]):
    """Hermetic Polyfactory builder for UserCreate payloads."""

    __model__ = UserCreate
    __set_as_default_factory_for_type__ = False

    email: str = "member@nordic.example.com"
    password: str | None = "validpass123"
    name: str | None = "Nordic Member"
    role: UserRole = UserRole.MEMBER
    organization_id: str | None = None
    is_active: bool = True
    language: SystemLocale = SystemLocale.EN
    theme_mode: str = "system"
    created_by: str | None = None


class _TokenDataFactory(ModelFactory[TokenData]):
    """Hermetic Polyfactory builder for TokenData claims."""

    __model__ = TokenData
    __set_as_default_factory_for_type__ = False

    email: str | None = "root@quorum.example.com"
    role: UserRole = UserRole.ROOT
    mfa: bool = True

    @classmethod
    def id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 user subject identifier.

        Returns:
            Canonical User Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 organization identifier.

        Returns:
            Canonical Organization Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)


@pytest.fixture
def identity_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a fresh stateful in-memory repository for hermetic IAM tests.

    Returns:
        Stateful InMemoryUnifiedWorkflowRepository instance.
    """
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_user_creator_protocol_structural_conformance_and_org_provisioning(
    identity_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Positive: verify UserCreatorProtocol conformance and stateful OrganizationService provisioning roundtrip."""
    assert protocols_all == ["UserCreatorProtocol"]

    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    user_service = UserService(user_repo=user_repo, org_repo=org_repo, use_firebase=False)

    user_creator: UserCreatorProtocol = user_service._create_user_internal
    assert isinstance(user_creator, UserCreatorProtocol)

    org_service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        use_firebase=False,
        user_creator=user_creator,
    )

    root_user = _UserModelFactory.build(
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
    )
    await identity_repo.create_user(root_user)
    root_token = _TokenDataFactory.build(
        id=root_user.id,
        email=root_user.email,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
    )
    org_payload = _OrganizationCreateFactory.build(
        name="Polaris Research Oy",
        admin_email="lead@polaris.example.com",
    )

    created_org = await org_service.create_organization(initiator=root_token, org_create=org_payload)
    assert _OPAQUE_ID_PATTERN.match(created_org.id) is not None

    persisted_org = await identity_repo.get_organization_model(created_org.id)
    assert persisted_org is not None
    assert Organization.model_validate(persisted_org.model_dump(mode="json")).id == created_org.id

    provisioned_users = await user_service.get_users_by_organization(created_org.id)
    assert len(provisioned_users) == 1
    admin_user = provisioned_users[0]
    assert _OPAQUE_ID_PATTERN.match(admin_user.id) is not None
    assert User.model_validate(admin_user.model_dump(mode="json")).id == admin_user.id
    assert admin_user.email == "lead@polaris.example.com"
    assert admin_user.role == UserRole.ADMIN
    assert admin_user.organization_id == created_org.id
    assert admin_user.created_by == root_user.id


@pytest.mark.asyncio
async def test_organization_service_missing_user_creator_protocol_raises_configuration_error(
    identity_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: OrganizationService without UserCreatorProtocol raises AppException(CONFIGURATION_ERROR)."""
    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    org_service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        use_firebase=False,
        user_creator=None,
    )

    root_token = _TokenDataFactory.build(role=UserRole.ROOT)
    org_payload = _OrganizationCreateFactory.build()

    with pytest.raises(AppException) as exc_info:
        await org_service.create_organization(initiator=root_token, org_create=org_payload)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_user_creator_protocol_unknown_creator_raises_resource_not_found(
    identity_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: invoking UserCreatorProtocol with nonexistent creator_id raises RESOURCE_NOT_FOUND."""
    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    user_service = UserService(user_repo=user_repo, org_repo=org_repo, use_firebase=False)
    user_creator: UserCreatorProtocol = user_service._create_user_internal

    missing_creator_id = generate_opaque_id(EntityPrefix.USER)
    payload = _UserCreateFactory.build()

    with pytest.raises(AppException) as exc_info:
        await user_creator(creator_id=missing_creator_id, user_data=payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_user_creator_protocol_cross_tenant_violation_raises_permission_denied(
    identity_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: non-ROOT creator targeting foreign organization via UserCreatorProtocol raises PERMISSION_DENIED."""
    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    user_service = UserService(user_repo=user_repo, org_repo=org_repo, use_firebase=False)
    user_creator: UserCreatorProtocol = user_service._create_user_internal

    org_a = _OrganizationModelFactory.build(name="Tenant Alpha")
    org_b = _OrganizationModelFactory.build(name="Tenant Beta")
    await identity_repo.create_organization(org_a)
    await identity_repo.create_organization(org_b)

    admin_a = _UserModelFactory.build(
        email="admin@alpha.example.com",
        role=UserRole.ADMIN,
        organization_id=org_a.id,
    )
    await identity_repo.create_user(admin_a)

    foreign_payload = _UserCreateFactory.build(
        email="intruder@beta.example.com",
        role=UserRole.MEMBER,
        organization_id=org_b.id,
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await user_creator(creator_id=admin_a.id, user_data=foreign_payload, force_org_id=None)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value


@pytest.mark.asyncio
async def test_user_creator_protocol_boundary_and_structural_rejection(
    identity_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative & BVA boundary: direct Protocol instantiation fails and password min_length=6 boundary is enforced."""
    protocol_type: type[object] = UserCreatorProtocol
    with pytest.raises(TypeError):
        protocol_type()

    assert not isinstance(object(), UserCreatorProtocol)

    with pytest.raises(ValidationError):
        UserCreate.model_validate(
            {
                "email": "short@nordic.example.com",
                "password": "abcde",
                "name": "Boundary Minus One",
                "role": UserRole.MEMBER,
                "organization_id": None,
                "is_active": True,
                "language": SystemLocale.EN,
                "theme_mode": "system",
            }
        )

    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    user_service = UserService(user_repo=user_repo, org_repo=org_repo, use_firebase=False)
    user_creator: UserCreatorProtocol = user_service._create_user_internal

    tenant_org = _OrganizationModelFactory.build(name="Boundary Org")
    await identity_repo.create_organization(tenant_org)
    root_user = _UserModelFactory.build(
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
    )
    await identity_repo.create_user(root_user)

    exact_min_payload = _UserCreateFactory.build(
        email="exact6@nordic.example.com",
        password="abcdef",
        role=UserRole.MEMBER,
    )
    created = await user_creator(root_user.id, exact_min_payload, force_org_id=tenant_org.id)
    assert created.organization_id == tenant_org.id
    fetched = await identity_repo.get_user(created.id)
    assert fetched is not None
    assert fetched.email == "exact6@nordic.example.com"

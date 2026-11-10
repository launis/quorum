"""Hermetic unit, negative fault-injection, and ISTQB boundary tests for auth repositories."""

from __future__ import annotations

import re
from datetime import UTC, datetime

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, generate_opaque_id
from backend_v2.models.enums import EntityPrefix, SystemLocale
from backend_v2.services.auth.repositories import (
    OrganizationRepository,
    UserRepository,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

__all__ = [
    "test_organization_repository_create_duplicate_id_raises_conflict_error",
    "test_organization_repository_crud_roundtrip_and_schema_parity",
    "test_organization_repository_missing_entity_negative_returns_none_and_false",
    "test_organization_repository_storage_fault_propagation_error",
    "test_repository_models_boundary_value_invalid_inputs_failure",
    "test_user_repository_create_duplicate_id_raises_conflict_error",
    "test_user_repository_crud_roundtrip_and_schema_parity",
    "test_user_repository_get_by_email_and_organization_scoping",
    "test_user_repository_get_by_firebase_uid_active_vs_soft_deleted_boundary",
    "test_user_repository_missing_entity_negative_returns_none_and_false",
    "test_user_repository_storage_fault_propagation_error",
]

_OPAQUE_ID_PATTERN: re.Pattern[str] = re.compile(OPAQUE_STRIPE_ID_REGEX)


class _OrganizationModelFactory(ModelFactory[Organization]):
    """Hermetic Polyfactory builder for Organization domain models."""

    __model__ = Organization
    __set_as_default_factory_for_type__ = False

    name: str = "Nordic Enterprise Oy"
    is_active: bool = True
    tier: str = "enterprise"
    subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    quota_limit: float = 500.0
    tpm_limit: int = 50000
    rpm_limit: int = 500
    slug: str | None = None
    contact_email: str | None = "admin@nordic.example.com"
    billing_id: str | None = "bill_nordic_001"

    @classmethod
    def id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 organization identifier.

        Returns:
            Canonical Organization Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def created_at(cls) -> datetime:
        """Generate a timezone-aware UTC creation timestamp.

        Returns:
            Current UTC datetime instance.
        """
        return datetime.now(UTC)

    @classmethod
    def allowed_email_domains(cls) -> list[str]:
        """Generate an empty email domain allowlist.

        Returns:
            Empty list of domain strings.
        """
        return []


class _UserModelFactory(ModelFactory[User]):
    """Hermetic Polyfactory builder for User domain models."""

    __model__ = User
    __set_as_default_factory_for_type__ = False

    email: str = "member@nordic.example.com"
    name: str | None = "Nordic Member"
    role: UserRole = UserRole.MEMBER
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
        """Generate a timezone-aware UTC creation timestamp.

        Returns:
            Current UTC datetime instance.
        """
        return datetime.now(UTC)


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a stateful in-memory unified repository for hermetic testing.

    Returns:
        Fresh InMemoryUnifiedWorkflowRepository instance.
    """
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_organization_repository_crud_roundtrip_and_schema_parity(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify OrganizationRepository create, get_by_id, list_all, update, and delete roundtrips."""
    org_repo = OrganizationRepository(mock_repo)
    org_alpha = _OrganizationModelFactory.build(name="Alpha Organization")
    org_beta = _OrganizationModelFactory.build(name="Beta Organization")

    created_alpha = await org_repo.create(org_alpha)
    await org_repo.create(org_beta)
    assert created_alpha.id == org_alpha.id
    assert _OPAQUE_ID_PATTERN.match(created_alpha.id) is not None

    fetched = await org_repo.get_by_id(org_alpha.id)
    assert fetched is not None
    reconstituted = Organization.model_validate(fetched.model_dump(mode="json"))
    assert reconstituted.id == org_alpha.id
    assert reconstituted.name == "Alpha Organization"

    all_orgs = await org_repo.list_all()
    assert {o.id for o in all_orgs} == {org_alpha.id, org_beta.id}

    update_payload = OrganizationUpdateDTO.model_validate_json('{"name": "Alpha Renamed", "tpm_limit": 75000}')
    updated_ok = await org_repo.update(org_alpha.id, update_payload)
    assert updated_ok is True

    refreshed = await org_repo.get_by_id(org_alpha.id)
    assert refreshed is not None
    validated_refresh = Organization.model_validate(refreshed.model_dump(mode="json"))
    assert validated_refresh.name == "Alpha Renamed"
    assert validated_refresh.tpm_limit == 75000

    deleted_ok = await org_repo.delete(org_alpha.id)
    assert deleted_ok is True
    assert await org_repo.get_by_id(org_alpha.id) is None


@pytest.mark.asyncio
async def test_organization_repository_missing_entity_negative_returns_none_and_false(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify OrganizationRepository returns None/False for nonexistent canonical organization IDs."""
    org_repo = OrganizationRepository(mock_repo)
    missing_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)

    assert await org_repo.get_by_id(missing_org_id) is None
    update_payload = OrganizationUpdateDTO.model_validate_json('{"name": "Ghost Org"}')
    assert await org_repo.update(missing_org_id, update_payload) is False
    assert await org_repo.delete(missing_org_id) is False


@pytest.mark.asyncio
async def test_organization_repository_create_duplicate_id_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: creating an Organization with an existing canonical ID raises ConflictError (409)."""
    org_repo = OrganizationRepository(mock_repo)
    existing_org = _OrganizationModelFactory.build(name="Original Tenant")
    await org_repo.create(existing_org)

    duplicate_org = _OrganizationModelFactory.build(id=existing_org.id, name="Duplicate Tenant")
    with pytest.raises(ConflictError) as exc_info:
        await org_repo.create(duplicate_org)

    assert isinstance(exc_info.value, AppException)
    assert exc_info.value.status_code == 409
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    persisted = await org_repo.get_by_id(existing_org.id)
    assert persisted is not None
    assert persisted.name == "Original Tenant"


@pytest.mark.asyncio
async def test_user_repository_crud_roundtrip_and_schema_parity(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify UserRepository create, get_by_id, update, list_all, and delete stateful roundtrips."""
    user_repo = UserRepository(mock_repo)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    user = _UserModelFactory.build(
        email="alice@nordic.example.com",
        name="Alice Original",
        organization_id=org_id,
    )

    created = await user_repo.create(user)
    assert created.id == user.id
    assert _OPAQUE_ID_PATTERN.match(created.id) is not None

    fetched = await user_repo.get_by_id(user.id)
    assert fetched is not None
    reconstituted = User.model_validate(fetched.model_dump(mode="json"))
    assert reconstituted.id == user.id
    assert reconstituted.name == "Alice Original"

    update_payload = UserUpdate.model_validate_json('{"name": "Alice Updated", "theme_mode": "dark"}')
    updated = await user_repo.update(user.id, update_payload)
    assert updated is not None
    validated_updated = User.model_validate(updated.model_dump(mode="json"))
    assert validated_updated.name == "Alice Updated"
    assert validated_updated.theme_mode == "dark"

    all_users = await user_repo.list_all()
    assert [u.id for u in all_users] == [user.id]

    deleted_ok = await user_repo.delete(user.id)
    assert deleted_ok is True
    assert await user_repo.get_by_id(user.id) is None


@pytest.mark.asyncio
async def test_user_repository_get_by_email_and_organization_scoping(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify UserRepository.get_by_email and get_by_organization tenant filtering."""
    user_repo = UserRepository(mock_repo)
    org_primary = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_secondary = generate_opaque_id(EntityPrefix.ORGANIZATION)

    user_one = _UserModelFactory.build(
        email="one@primary.example.com",
        role=UserRole.ADMIN,
        organization_id=org_primary,
    )
    user_two = _UserModelFactory.build(
        email="two@primary.example.com",
        role=UserRole.MEMBER,
        organization_id=org_primary,
    )
    user_foreign = _UserModelFactory.build(
        email="foreign@secondary.example.com",
        role=UserRole.MEMBER,
        organization_id=org_secondary,
    )
    await user_repo.create(user_one)
    await user_repo.create(user_two)
    await user_repo.create(user_foreign)

    by_email = await user_repo.get_by_email("one@primary.example.com")
    assert by_email is not None
    assert by_email.id == user_one.id
    assert await user_repo.get_by_email("absent@primary.example.com") is None

    scoped_users = await user_repo.get_by_organization(org_primary)
    assert {u.id for u in scoped_users} == {user_one.id, user_two.id}


@pytest.mark.asyncio
async def test_user_repository_get_by_firebase_uid_active_vs_soft_deleted_boundary(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify UserRepository.get_by_firebase_uid returns active user and excludes soft-deleted or missing UIDs."""
    user_repo = UserRepository(mock_repo)
    active_user = _UserModelFactory.build(
        email="fb_active@nordic.example.com",
        firebase_uid="a",
        deleted_at=None,
    )
    max_uid = "f" * 128
    max_boundary_user = _UserModelFactory.build(
        email="fb_max@nordic.example.com",
        firebase_uid=max_uid,
        deleted_at=None,
    )
    soft_deleted_user = _UserModelFactory.build(
        email="fb_deleted@nordic.example.com",
        is_active=False,
        firebase_uid="fb_uid_soft_deleted",
        deleted_at=datetime.now(UTC),
    )
    await user_repo.create(active_user)
    await user_repo.create(max_boundary_user)
    await user_repo.create(soft_deleted_user)

    found_min = await user_repo.get_by_firebase_uid("a")
    assert found_min is not None
    assert found_min.id == active_user.id

    found_max = await user_repo.get_by_firebase_uid(max_uid)
    assert found_max is not None
    assert found_max.id == max_boundary_user.id

    assert await user_repo.get_by_firebase_uid("fb_uid_soft_deleted") is None
    assert await user_repo.get_by_firebase_uid("fb_uid_nonexistent") is None


@pytest.mark.asyncio
async def test_user_repository_missing_entity_negative_returns_none_and_false(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify UserRepository returns None/False for nonexistent canonical user IDs."""
    user_repo = UserRepository(mock_repo)
    missing_user_id = generate_opaque_id(EntityPrefix.USER)

    assert await user_repo.get_by_id(missing_user_id) is None
    update_payload = UserUpdate.model_validate_json('{"name": "Missing User"}')
    assert await user_repo.update(missing_user_id, update_payload) is None
    assert await user_repo.delete(missing_user_id) is False


@pytest.mark.asyncio
async def test_user_repository_create_duplicate_id_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: creating a User with an existing canonical ID raises ConflictError (409)."""
    user_repo = UserRepository(mock_repo)
    original_user = _UserModelFactory.build(email="first@nordic.example.com")
    await user_repo.create(original_user)

    duplicate_user = _UserModelFactory.build(id=original_user.id, email="second@nordic.example.com")
    with pytest.raises(ConflictError) as exc_info:
        await user_repo.create(duplicate_user)

    assert isinstance(exc_info.value, AppException)
    assert exc_info.value.status_code == 409
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
    persisted = await user_repo.get_by_id(original_user.id)
    assert persisted is not None
    assert persisted.email == "first@nordic.example.com"


@pytest.mark.asyncio
async def test_organization_repository_storage_fault_propagation_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: OrganizationRepository propagates typed AppException storage faults cleanly."""
    org_repo = OrganizationRepository(mock_repo)
    storage_err = AppException(
        message="Simulated PostgreSQL connection timeout on organizations",
        status_code=503,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    mock_repo.inject_fault("get_organization", storage_err, trigger_count=1)
    try:
        with pytest.raises(AppException) as exc_info:
            await org_repo.get_by_id(generate_opaque_id(EntityPrefix.ORGANIZATION))
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        mock_repo.clear_faults()


@pytest.mark.asyncio
async def test_user_repository_storage_fault_propagation_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: UserRepository propagates typed AppException storage faults cleanly."""
    user_repo = UserRepository(mock_repo)
    storage_err = AppException(
        message="Simulated PostgreSQL connection timeout on users",
        status_code=503,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    mock_repo.inject_fault("list_users", storage_err, trigger_count=1)
    try:
        with pytest.raises(AppException) as exc_info:
            await user_repo.get_by_firebase_uid("fb_uid_probe")
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        mock_repo.clear_faults()


def test_repository_models_boundary_value_invalid_inputs_failure() -> None:
    """Negative ISTQB BVA: reject min-1 and max+1 boundary violations on Organization and User schemas."""
    valid_min_org = _OrganizationModelFactory.build(quota_limit=0.0, tpm_limit=1000, rpm_limit=1)
    assert valid_min_org.quota_limit == 0.0
    assert valid_min_org.tpm_limit == 1000
    assert valid_min_org.rpm_limit == 1

    with pytest.raises(ValidationError):
        Organization.model_validate(
            {
                **valid_min_org.model_dump(mode="python"),
                "tpm_limit": 999,
            }
        )

    with pytest.raises(ValidationError):
        Organization.model_validate(
            {
                **valid_min_org.model_dump(mode="python"),
                "rpm_limit": 0,
            }
        )

    with pytest.raises(ValidationError):
        Organization.model_validate(
            {
                **valid_min_org.model_dump(mode="python"),
                "quota_limit": -0.01,
            }
        )

    valid_user = _UserModelFactory.build(firebase_uid="x")
    with pytest.raises(ValidationError):
        User.model_validate(
            {
                **valid_user.model_dump(mode="python"),
                "firebase_uid": "",
            }
        )

    with pytest.raises(ValidationError):
        User.model_validate(
            {
                **valid_user.model_dump(mode="python"),
                "firebase_uid": "x" * 129,
            }
        )

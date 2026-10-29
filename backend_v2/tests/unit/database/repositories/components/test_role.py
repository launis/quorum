"""Unit tests for RoleRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.role import RoleRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Role


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> RoleRepositoryImpl:
    """Provide a RoleRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured RoleRepositoryImpl instance.
    """
    return RoleRepositoryImpl(driver)


@pytest.fixture
def sample_role() -> Role:
    """Provide a valid Role domain model fixture.

    Returns:
        Validated Role domain model.
    """
    return Role(
        id="rol_1234567890abcdef",
        name=I18nText(translations={"en": "Executive Coach", "fi": "Johdon Valmentaja"}),
        model_role="analyst_model",
        type="role",
    )


@pytest.mark.asyncio
async def test_role_crud_roundtrip(
    repo: RoleRepositoryImpl,
    sample_role: Role,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for roles."""
    created_id = await repo.create_role(sample_role)
    assert created_id == sample_role.id

    fetched = await repo.get_role_by_id(sample_role.id)
    assert fetched is not None
    assert isinstance(fetched, Role)
    assert fetched.id == sample_role.id
    assert fetched.model_role == "analyst_model"

    all_roles = await repo.get_all_roles()
    assert len(all_roles) == 1
    assert all_roles[0].id == sample_role.id

    updated_role = sample_role.model_copy(update={"model_role": "critic_model"})
    updated_id = await repo.update_role(sample_role.id, updated_role)
    assert updated_id == sample_role.id

    refetched = await repo.get_role_by_id(sample_role.id)
    assert refetched is not None
    assert isinstance(refetched, Role)
    assert refetched.model_role == "critic_model"

    deleted = await repo.delete_role(sample_role.id)
    assert deleted is True
    assert await repo.get_role_by_id(sample_role.id) is None
    assert await repo.get_all_roles() == []


@pytest.mark.asyncio
async def test_update_role_not_found(
    repo: RoleRepositoryImpl,
    sample_role: Role,
) -> None:
    """Negative: update_role raises ResourceNotFoundError if role does not exist."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.update_role("rol_0000000000000000", sample_role)

    assert exc_info.value.details["resource_type"] == "Role"
    assert exc_info.value.details["resource_id"] == "rol_0000000000000000"


@pytest.mark.asyncio
async def test_delete_role_not_found(
    repo: RoleRepositoryImpl,
) -> None:
    """Negative boundary: delete_role returns False when role does not exist."""
    assert await repo.delete_role("rol_0000000000000000") is False


@pytest.mark.asyncio
async def test_get_role_by_id_corrupted_raises_app_exception(
    repo: RoleRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_role_by_id raises AppException(500) on corrupted record."""
    await driver.upsert(
        "components",
        {"id": "rol_1111111111111111", "type": "role"},
        "rol_1111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_role_by_id("rol_1111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "rol_1111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_roles_corrupted_with_id_raises_app_exception(
    repo: RoleRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_all_roles raises AppException(500) when stored record with ID is invalid."""
    await driver.upsert(
        "components",
        {"id": "rol_2222222222222222", "type": "role"},
        "rol_2222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_roles()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "rol_2222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_roles_corrupted_without_id_raises_app_exception(
    repo: RoleRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_roles logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(
        collection: str, *args: object, **kwargs: object
    ) -> list[dict[str, str]]:
        return [{"type": "role"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_roles()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message

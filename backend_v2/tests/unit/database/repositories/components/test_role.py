"""Unit tests for RoleRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.role import RoleRepositoryImpl
from backend_v2.exceptions import AppException, ResourceNotFoundError


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "rol_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> RoleRepositoryImpl:
    """Provides a RoleRepositoryImpl instance with the mocked driver."""
    return RoleRepositoryImpl(mock_driver)


@pytest.fixture
def valid_role_doc() -> dict:
    """Valid Role document fixture."""
    return {
        "id": "rol_1234567890abcdef",
        "name": {"translations": {"en": "Executive Coach", "fi": "Johdon Valmentaja"}},
        "model_role": "analyst_model",
        "type": "role",
    }


@pytest.mark.asyncio
async def test_role_crud_lifecycle(repo: RoleRepositoryImpl, mock_driver: AsyncMock, valid_role_doc: dict) -> None:
    """Positive: tests role listing, getting by ID, creation, update, and deletion."""
    mock_driver.query.return_value = [valid_role_doc]
    mock_driver.get.return_value = valid_role_doc

    roles = await repo.get_all_roles()
    assert len(roles) == 1
    assert roles[0].id == "rol_1234567890abcdef"

    role = await repo.get_role_by_id("rol_1234567890abcdef")
    assert role is not None
    assert role.model_role == "analyst_model"

    assert await repo.create_role(valid_role_doc) == "rol_1234567890abcdef"
    assert await repo.update_role("rol_1234567890abcdef", {"model_role": "critic_model"}) == "rol_1234567890abcdef"
    assert await repo.delete_role("rol_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_role_parsing_failures(repo: RoleRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: corrupted role data raises AppException."""
    corrupted_doc = {"id": "invalid_id", "type": "role"}
    mock_driver.query.return_value = [corrupted_doc]
    mock_driver.get.return_value = corrupted_doc

    with pytest.raises(AppException):
        await repo.get_all_roles()

    with pytest.raises(AppException):
        await repo.get_role_by_id("invalid_id")


@pytest.mark.asyncio
async def test_role_not_found_branches(repo: RoleRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: verifies behavior when role is missing."""
    mock_driver.get.return_value = None

    assert await repo.get_role_by_id("rol_missing") is None

    with pytest.raises(ResourceNotFoundError):
        await repo.update_role("rol_missing", {"model_role": "critic_model"})

    assert await repo.delete_role("rol_missing") is False

"""Tests for ComponentRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import PromptBlock


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ComponentRepositoryImpl:
    """Provides a ComponentRepositoryImpl instance with the mocked driver."""
    return ComponentRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_get_all_components(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test retrieving all components with and without filters."""
    # Without exclude
    mock_driver.query.return_value = [{"id": "c1", "type": "T1"}, {"id": "c2", "type": "T2"}]
    res = await repo.get_all_components(type="T1")
    assert len(res) == 2
    mock_driver.query.assert_called_once()

    # With exclude
    mock_driver.query.reset_mock()
    mock_driver.query.return_value = [{"id": "c1", "type": "T1"}, {"id": "c2", "type": "T2"}]
    res2 = await repo.get_all_components(type="T1", exclude_types=["T2"])
    assert len(res2) == 1
    assert res2[0]["id"] == "c1"


@pytest.mark.asyncio
async def test_get_component_by_id(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test getting component by ID."""
    mock_driver.get.return_value = {"id": "c1"}
    res = await repo.get_component_by_id("c1")
    assert res == {"id": "c1"}
    mock_driver.get.assert_called_once_with("components", "c1")


@pytest.mark.asyncio
async def test_get_component_by_name(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test getting component by name."""
    mock_driver.query.return_value = [{"id": "c1", "name": "Test Name"}]
    res = await repo.get_component_by_name("Test Name")
    assert res == {"id": "c1", "name": "Test Name"}
    mock_driver.query.assert_called_once()


@pytest.mark.asyncio
async def test_update_component_metadata(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test updating metadata for component."""
    mock_driver.get.return_value = {"id": "c1"}
    mock_driver.update.return_value = True
    res = await repo.update_component_metadata("c1", "mod", "cls")
    assert res is True
    mock_driver.update.assert_called_once_with("components", "c1", {"module": "mod", "class_name": "cls"})


@pytest.mark.asyncio
async def test_update_component_metadata_not_found(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test updating metadata for non-existent component."""
    mock_driver.get.return_value = None
    res = await repo.update_component_metadata("c1", "mod", "cls")
    assert res is False


@pytest.mark.asyncio
async def test_create_register_update_delete_component(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test basic CRUD for generic components."""
    # Create/Register
    mock_driver.upsert.return_value = "c1"
    res1 = await repo.create_component({"id": "c1"})
    res2 = await repo.register_component({"id": "c1"})
    assert res1 == "c1"
    assert res2 == "c1"

    # Update
    mock_driver.get.return_value = {"id": "c1"}
    mock_driver.update.return_value = True
    res3 = await repo.update_component("c1", {"foo": "bar"})
    assert res3 == "c1"

    # Delete
    mock_driver.delete.return_value = True
    res4 = await repo.delete_component("c1")
    assert res4 is True


@pytest.mark.asyncio
async def test_delete_component_not_found(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test deleting non-existent component."""
    mock_driver.get.return_value = None
    res = await repo.delete_component("c1")
    assert res is False


@pytest.mark.asyncio
async def test_get_components_using_dimension(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test get components using dimension logic."""
    mock_driver.query.return_value = [
        {"id": "m1", "type": "evaluation_matrix", "content": {"criteria": [{"dimension_id": "dim1"}]}},
        {"id": "m2", "type": "evaluation_matrix", "content": {"criteria": [{"dimension_id": "dim2"}]}},
        {"id": "m3", "type": "evaluation_matrix"},  # Missing content
        {"id": "m4", "type": "evaluation_matrix", "content": "not_dict"},
    ]
    res = await repo.get_components_using_dimension("dim1")
    assert res == ["m1"]

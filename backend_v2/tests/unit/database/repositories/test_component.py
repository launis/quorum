"""Tests for ComponentRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.exceptions import AppException


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
async def test_agent_crud(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for Agents."""
    mock_driver.get.return_value = {"id": "a1"}
    mock_driver.query.return_value = [{"id": "a1"}]
    mock_driver.upsert.return_value = "a1"
    mock_driver.delete.return_value = True

    assert await repo.get_agent_by_id("a1") == {"id": "a1"}
    assert await repo.get_all_agents() == [{"id": "a1"}]
    assert await repo.create_agent({"id": "a1"}) == "a1"
    assert await repo.delete_agent("a1") is True


@pytest.mark.asyncio
async def test_update_agent(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test versioned update of Agent."""
    mock_driver.get.return_value = {"id": "a1_v1", "version": 1}
    repo._increment_version = MagicMock(return_value=("a1", "a1_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_agent("a1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_task_blueprint_crud(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for TaskBlueprints."""
    mock_driver.get.return_value = {"id": "tb1"}
    mock_driver.query.return_value = [{"id": "tb1"}]
    mock_driver.upsert.return_value = "tb1"
    mock_driver.delete.return_value = True

    assert await repo.get_task_blueprint_by_id("tb1") == {"id": "tb1"}
    assert await repo.get_all_task_blueprints() == [{"id": "tb1"}]
    assert await repo.create_task_blueprint({"id": "tb1"}) == "tb1"
    assert await repo.delete_task_blueprint("tb1") is True


@pytest.mark.asyncio
async def test_update_task_blueprint(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test versioned update of TaskBlueprint."""
    mock_driver.get.return_value = {"id": "tb1_v1", "version": 1}
    repo._increment_version = MagicMock(return_value=("tb1", "tb1_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_task_blueprint("tb1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_output_profile_crud(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for OutputProfiles."""
    mock_driver.get.return_value = {"id": "op1"}
    mock_driver.query.return_value = [{"id": "op1"}]
    mock_driver.upsert.return_value = "op1"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True

    assert await repo.get_output_profile_by_id("op1") == {"id": "op1"}
    assert await repo.get_all_output_profiles() == [{"id": "op1"}]
    assert await repo.create_output_profile({"id": "op1"}) == "op1"
    assert await repo.update_output_profile("op1", {"foo": "bar"}) is True
    assert await repo.delete_output_profile("op1") is True


@pytest.mark.asyncio
async def test_get_all_output_profiles_models_failure(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test parsing failure for OutputProfiles models."""
    mock_driver.query.return_value = [{"invalid": "data"}]
    with pytest.raises(AppException) as exc:
        await repo.get_all_output_profiles_models()
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_prompt_block_crud(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for PromptBlocks."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "pb1"}]
    mock_driver.upsert.return_value = "pb1"

    assert await repo.get_prompt_block_by_id("pb1") == {"id": "pb1"}
    assert await repo.get_prompt_block("pb1") == {"id": "pb1"}
    assert await repo.get_all_prompt_blocks() == [{"id": "pb1"}]
    assert await repo.create_prompt_block({"id": "pb1"}) == "pb1"


@pytest.mark.asyncio
async def test_update_prompt_block(
    repo: ComponentRepositoryImpl, mock_driver: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test versioned update of PromptBlock."""
    mock_driver.get.return_value = {"id": "pb1_v1", "version": 1}
    # Mock _increment_version
    repo._increment_version = MagicMock(return_value=("pb1", "pb1_v2", 2))  # type: ignore[method-assign]

    res = await repo.update_prompt_block("pb1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.update.assert_called_with("prompt_blocks", "pb1_v1", {"is_latest": False})

    # Verify upsert call
    args, kwargs = mock_driver.upsert.call_args
    assert args[0] == "prompt_blocks"
    assert args[1]["id"] == "pb1_v2"
    assert args[1]["version"] == 2
    assert args[1]["foo"] == "bar"


@pytest.mark.asyncio
async def test_update_prompt_block_not_found(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test updating non-existent PromptBlock."""
    mock_driver.get.return_value = None
    res = await repo.update_prompt_block("pb1", {})
    assert res is False


@pytest.mark.asyncio
async def test_delete_prompt_block_blocked_by_usage(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test delete prompt block when blocked by step usage."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "step1", "prompt_blocks": ["pb1"]}]

    with pytest.raises(AppException) as exc:
        await repo.delete_prompt_block("pb1", force_delete=False)

    assert exc.value.status_code == 400
    assert "delete blocked" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_delete_prompt_block_success(repo: ComponentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test successful delete prompt block."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "step1", "prompt_blocks": ["pb2"]}]
    mock_driver.delete.return_value = True

    assert await repo.delete_prompt_block("pb1") is True

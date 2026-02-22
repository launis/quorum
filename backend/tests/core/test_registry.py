from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from backend.core.registry import TaskRegistry
from backend.exceptions import AppException, ErrorCodes, status


# Mock BaseAgent for testing
class MockAgent:
    def __init__(self):
        pass

    async def execute(self, **kwargs):
        return {"result": "success"}


class MockInput(BaseModel):
    data: str


class MockOutput(BaseModel):
    result: str


def test_register_agent_instantiation_failure():
    """Verify registry raises AppException if agent cannot be instantiated."""

    class BrokenAgent:
        def __init__(self):
            raise ValueError("I am broken")

    with pytest.raises(AppException) as exc:
        TaskRegistry.register_agent(task_keys=["broken_task"], agent_cls=BrokenAgent, output_model=MockOutput)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR
    assert "I am broken" in str(exc.value.details.get("original_error"))


@pytest.mark.asyncio
async def test_agent_wrapper_configuration_failure():
    """Verify wrapper raises AppException if dependency resolution fails."""
    # We need to register a valid agent first to get the wrapper
    TaskRegistry.register_agent(task_keys=["config_fail_task"], agent_cls=MockAgent, output_model=MockOutput)

    task_def = TaskRegistry.get("config_fail_task")
    assert task_def is not None
    wrapper = task_def.handler

    # Mock get_async_repository to fail
    # Since the import happens inside the function, we patch the source module
    with patch("backend.dependencies.get_async_repository", side_effect=ValueError("Dependency Fail")):
        with pytest.raises(AppException) as exc:
            await wrapper(MockInput(data="test"))

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.value.error_code == ErrorCodes.AGENT_NOT_CONFIGURED
    assert "Dependency Fail" in str(exc.value.details.get("original_error"))


@pytest.mark.asyncio
async def test_agent_wrapper_model_override_failure():
    """Verify wrapper raises AppException if model override fails resolution."""
    TaskRegistry.register_agent(task_keys=["override_fail_task"], agent_cls=MockAgent, output_model=MockOutput)

    task_def = TaskRegistry.get("override_fail_task")
    assert task_def is not None
    wrapper = task_def.handler

    # Mock dependencies to pass until model resolution
    mock_repo = MagicMock()
    mock_registry = AsyncMock()
    # resolve_model_config success
    config_mock = MagicMock()
    config_mock.model_dump.return_value = {"model_name": "default"}
    mock_registry.resolve_model_config.return_value = config_mock
    # resolve_model_name failure
    mock_registry.resolve_model_name.side_effect = ValueError("Invalid Model")

    with patch("backend.dependencies.get_async_repository", return_value=mock_repo):
        with patch("backend.services.agent_registry.AgentRegistry", return_value=mock_registry):
            with pytest.raises(AppException) as exc:
                await wrapper(MockInput(data="test"), execution_config={"model": "bad_model"})

            assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD
            assert "Invalid Model" in str(exc.value.details.get("original_error"))

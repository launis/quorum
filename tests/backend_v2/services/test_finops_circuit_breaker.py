from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionCreate, WorkflowInputs
from backend_v2.services.execution import ExecutionService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy


class DummyNodeStrategy(NodeStrategy):
    async def execute(self, *args: Any, **kwargs: Any) -> list[Any]:
        return []


@pytest.fixture
def repo_mock() -> AsyncMock:
    mock = AsyncMock()
    mock.get_step_by_id = AsyncMock(return_value={"type": "llm", "model_strategy": "openai"})
    mock.get_workflow_by_id = AsyncMock(
        return_value={
            "id": "wf_1234567890abcdef",
            "slug": "test_wf",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test desc"}},
            "status": "published",
            "version": 1,
            "organization_id": "test_org",
            "steps": [],
            "expected_inputs": [],
            "output_profiles": {},
            "default_profile_id": "default",
        }
    )
    return mock


@pytest.fixture
def token_data() -> TokenData:
    return TokenData(id="usr_12345678", role=UserRole.MEMBER, organization_id="test_org", email="test@example.com")


@pytest.mark.asyncio
async def test_start_execution_circuit_breaker(repo_mock: AsyncMock, token_data: TokenData) -> None:
    """Tests that starting a new execution fails fast if quota is exceeded (Pre-flight)."""
    # Create the service with a mocked abstract caller (Executor isn't used here because execution start pushes to Arq)
    service = ExecutionService(repo=repo_mock, executor=AsyncMock())

    with patch("backend_v2.services.usage_service.UsageService") as UsageServiceMock:
        instance = UsageServiceMock.return_value
        instance.check_quota = AsyncMock(return_value=False)

        # Valid execution payload mapped to the generic workflow Inputs structure
        payload = ExecutionCreate(
            workflow_id="wf_1234567890abcdef", raw_inputs=WorkflowInputs.model_validate({}), target_locale="en"
        )
        arq_pool = AsyncMock()

        # Act & Assert
        with pytest.raises(AppException) as exc:
            await service.start_execution(initiator=token_data, payload=payload, arq_pool=arq_pool)

        assert exc.value.status_code == 402
        assert exc.value.details["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert "exceeded its execution quota" in str(exc.value.message)

        # Ensure that the job was NEVER queued
        arq_pool.enqueue_job.assert_not_called()


@pytest.mark.asyncio
async def test_worker_cutoff_circuit_breaker(repo_mock: AsyncMock) -> None:
    """Tests that mid-flight executions correctly halt if quota limit is reached (Worker Cut-off)."""
    strategy = DummyNodeStrategy(repository=repo_mock, prompt_compiler=None)

    with patch("backend_v2.services.usage_service.UsageService") as UsageServiceMock:
        instance = UsageServiceMock.return_value
        instance.check_quota = AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(AppException) as exc:
            await strategy.assert_quota("test_org")

        assert exc.value.status_code == 402
        assert exc.value.details["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert "ran out of quota mid-execution" in str(exc.value.message)


@pytest.mark.asyncio
async def test_worker_cutoff_circuit_breaker_pass(repo_mock: AsyncMock) -> None:
    """Tests that executions continue normally if quota is within limits."""
    strategy = DummyNodeStrategy(repository=repo_mock, prompt_compiler=None)

    with patch("backend_v2.services.usage_service.UsageService") as UsageServiceMock:
        instance = UsageServiceMock.return_value
        instance.check_quota = AsyncMock(return_value=True)  # Quota safe

        # Act & Assert
        try:
            await strategy.assert_quota("test_org")
        except Exception as e:
            pytest.fail(f"assert_quota raised an exception unexpectedly: {e}")

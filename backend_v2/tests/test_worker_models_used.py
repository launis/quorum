from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from pydantic import JsonValue

from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers import execute_workflow_job


@pytest.mark.asyncio
async def test_worker_preserves_models_used() -> None:
    """Test that execute_workflow_job does not overwrite the models_used
    dict with an empty dict, but preserves what the engine returns.
    """
    # 1. Arrange Mocks & Typed Fake Persistence
    mock_engine = AsyncMock()
    mock_repository = InMemoryUnifiedWorkflowRepository()
    mock_redis = AsyncMock()

    ctx = {"engine": mock_engine, "repository": mock_repository, "redis": mock_redis}

    workflow_id = "wor_a1b2c3d4e5f678901234"
    execution_id = "exe_a1b2c3d4e5f678901234"
    inputs: dict[str, JsonValue] = {}

    # Seed typed Workflow
    mock_workflow = Workflow(
        id=workflow_id,
        name="Test Workflow",
        status="active",
        version=1,
        slug="test-wf",
        description="Test WF",
        default_profile_id="prf_a1b2c3d4e5f67890",
        default_strictness_level=1,
        model_registry_id="sys_1111222233334444",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    await mock_repository.save_workflow(mock_workflow)

    # Seed typed ExecutionRecord
    mock_initial_record = ExecutionRecord(
        id=execution_id,
        workflow_id=workflow_id,
        status=ExecutionStatus.RUNNING,
        output_profile_id="prf_a1b2c3d4e5f67890",
        target_locale="fi",
        metadata=ExecutionMetadata(),
        models_used={},
        created_at=datetime(2026, 6, 16, 12, 0, 0, tzinfo=timezone.utc),
        created_by="usr_a1b2c3d4e5f678901234",
        organization_id="org_a1b2c3d4e5f678901234",
    )
    await mock_repository.save_execution(mock_initial_record)

    mock_updated_record = ExecutionRecord(
        id=execution_id,
        workflow_id=workflow_id,
        status=ExecutionStatus.RUNNING,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        output_profile_id="prf_test",
        models_used={"gemini-2.5-flash": 1500},
        created_at=datetime.now(timezone.utc),
        created_by="usr_a1b2c3d4e5f678901234",
        organization_id="org_a1b2c3d4e5f678901234",
    )
    mock_engine.execute_workflow.return_value = mock_updated_record

    # 2. Act
    await execute_workflow_job(ctx, workflow_id, inputs, execution_id=execution_id)

    # 3. Assert state persistence
    saved_record = await mock_repository.get_execution(execution_id)
    assert saved_record is not None, "ExecutionRecord not found in repository"
    assert saved_record.models_used == {"gemini-2.5-flash": 1500}, (
        f"Bug reproduced: models_used was overwritten! Found: {saved_record.models_used}"
    )

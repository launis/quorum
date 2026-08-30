from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.enums import ExecutionStatus
from backend_v2.worker import execute_workflow_job


@pytest.mark.asyncio
async def test_worker_preserves_models_used() -> None:
    """Test that execute_workflow_job does not overwrite the models_used
    dict with an empty dict, but preserves what the engine returns.
    """
    # 1. Arrange Mocks
    mock_engine = AsyncMock()
    mock_repository = AsyncMock()
    mock_redis = AsyncMock()

    ctx = {"engine": mock_engine, "repository": mock_repository, "redis": mock_redis}

    workflow_id = "wor_a1b2c3d4e5f678901234"
    execution_id = "exe_a1b2c3d4e5f678901234"
    inputs: dict[str, Any] = {}

    # Mock workflow dict returned by get_workflow
    mock_repository.get_workflow.return_value = {
        "id": workflow_id,
        "name": "Test Workflow",
        "status": "active",
        "version": 1,
        "slug": "test-wf",
        "description": "Test WF",
        "default_profile_id": "prf_a1b2c3d4e5f67890",
        "default_strictness_level": 1,
        "default_scoring_strategy": "AVERAGE",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "steps": [],
    }

    # Mock execution record returned by get_execution
    mock_repository.get_execution.return_value = {
        "id": execution_id,
        "workflow_id": workflow_id,
        "status": "RUNNING",
        "output_profile_id": "prf_a1b2c3d4e5f67890",
        "target_locale": "fi",
        "metadata": {"target_locale": "fi"},
        "models_used": {},
        "created_at": "2026-06-16T12:00:00Z",
        "created_by": "usr_a1b2c3d4e5f678901234",
        "organization_id": "org_a1b2c3d4e5f678901234",
    }

    mock_repository.get_output_profile_by_id.return_value = None

    from datetime import datetime, timezone

    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.models.v2_core import ExecutionRecord

    mock_updated_record = ExecutionRecord(
        id=execution_id,
        workflow_id=workflow_id,
        status=ExecutionStatus.RUNNING,
        target_locale="fi",
        metadata=ExecutionMetadata(target_locale="fi"),
        output_profile_id="prf_test",
        models_used={"gemini-2.5-flash": 1500},
        created_at=datetime.now(timezone.utc),
        created_by="usr_a1b2c3d4e5f678901234",
        organization_id="org_a1b2c3d4e5f678901234",
    )
    mock_engine.execute_workflow.return_value = mock_updated_record

    # 2. Act
    await execute_workflow_job(ctx, workflow_id, inputs, execution_id=execution_id)

    # 3. Assert
    # Check that update_execution was called with the preserved models_used, not an empty dict
    update_calls = mock_repository.update_execution.call_args_list
    assert len(update_calls) > 0, "update_execution was never called"

    # Find the call where status is 'completed' or 'running' at the end
    last_call = update_calls[-1]
    args, kwargs = last_call

    # The payload is the second argument
    update_payload = args[1]

    assert "models_used" in update_payload, "models_used missing from update payload"
    assert update_payload["models_used"] == {"gemini-2.5-flash": 1500}, (
        f"Bug reproduced: models_used was overwritten! Found: {update_payload['models_used']}"
    )

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.archival import retrieve_precedent_hook
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord


@pytest.fixture
def mock_deps() -> HookDependencies:
    return HookDependencies(
        repository=AsyncMock(),
        search_client=AsyncMock(),
    )


def create_mock_execution(
    with_judge: bool = True, invalid_judge: bool = False, missing_updated_at: bool = False
) -> ExecutionRecord:  # noqa: E501
    event_id = uuid.uuid4()

    # Valid JudgeOutput dict
    judge_content = {
        "thought_process": "Thinking...",
        "conclusion": "Done",
        "confidence_score": 0.9,
        "matrix_id": "m123",
        "scale_min": 0.0,
        "scale_max": 5.0,
        "score_card": {
            "agent_name": "Standard Judge",
            "total_score": 4.5,
            "max_score": 5,
            "verdict": "Great job",
            "dimensions": [{"dimension_id": "dim1", "dimension_label": "Analysis", "score": 4.5, "reasoning": "Good"}],
            "scale_min": 0.0,
            "scale_max": 5.0,
        },
    }

    if invalid_judge:
        # Missing mandatory fields like matrix_id
        judge_content = {"invalid": "schema"}

    trace_events = []
    if with_judge:
        trace_events.append(
            TraceEvent(event_id=event_id, step_name="step_judge_cognitive", event_type="output", content=judge_content)
        )

    if missing_updated_at:
        return ExecutionRecord.model_construct(
            id=f"exe_{uuid.uuid4().hex[:16]}",
            workflow_id="wf_123",
            status=ExecutionStatus.COMPLETED,
            execution_trace=trace_events,
            created_at=datetime.now(timezone.utc),
            updated_at=None,  # type: ignore[arg-type]
            completed_at=datetime.now(timezone.utc),
        )

    record = ExecutionRecord(
        id=f"exe_{uuid.uuid4().hex[:16]}",
        workflow_id="wf_123",
        status=ExecutionStatus.COMPLETED,
        execution_trace=trace_events,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )

    return record


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_success(mock_deps: HookDependencies) -> None:
    """Test successful retrieval and formatting of precedents."""
    from typing import cast

    cast(AsyncMock, mock_deps.repository.get_recent_completed_executions).return_value = [
        create_mock_execution(),
        create_mock_execution(),
    ]

    state = HookState(
        execution_id="exe_current",
        workflow_id="wf_123",
        step_id="step_archivist",
        metadata={},
        global_context_vars={},
        inputs={},
    )

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = await cast(Awaitable[HookResult], retrieve_precedent_hook(state, mock_deps))
    assert result.success is True
    assert result.state_delta is not None
    assert "archivist_precedents" in result.state_delta

    precedents = result.state_delta["archivist_precedents"]
    assert len(precedents) == 2
    assert "id" in precedents[0]
    assert "scores" in precedents[0]
    assert "Cognitive: 4.50" in precedents[0]["scores"]


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_no_repository() -> None:
    """Test failure when repository is not injected."""
    from typing import Any, cast

    deps = HookDependencies(repository=cast(Any, None), search_client=AsyncMock())
    state = HookState(
        execution_id="exe_current",
        workflow_id="wf_123",
        step_id="step_archivist",
        metadata={},
        global_context_vars={},
        inputs={},
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        from collections.abc import Awaitable
        from typing import cast

        from backend_v2.core.hook_registry import HookResult

        await cast(Awaitable[HookResult], retrieve_precedent_hook(state, deps))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_invalid_output_schema(mock_deps: HookDependencies) -> None:
    """Test Fail-Fast when repository returns raw dicts instead of Models."""
    from typing import cast

    cast(AsyncMock, mock_deps.repository.get_recent_completed_executions).return_value = [{"id": "not_a_model"}]
    state = HookState(
        execution_id="exe_current",
        workflow_id="wf_123",
        step_id="step_archivist",
        metadata={},
        global_context_vars={},
        inputs={},
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        from collections.abc import Awaitable
        from typing import cast

        from backend_v2.core.hook_registry import HookResult

        await cast(Awaitable[HookResult], retrieve_precedent_hook(state, mock_deps))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_state_integrity_error(mock_deps: HookDependencies) -> None:
    """Test Fail-Fast when an execution is missing updated_at."""
    from typing import cast

    cast(AsyncMock, mock_deps.repository.get_recent_completed_executions).return_value = [
        create_mock_execution(missing_updated_at=True)
    ]
    state = HookState(
        execution_id="exe_current",
        workflow_id="wf_123",
        step_id="step_archivist",
        metadata={},
        global_context_vars={},
        inputs={},
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        from collections.abc import Awaitable
        from typing import cast

        from backend_v2.core.hook_registry import HookResult

        await cast(Awaitable[HookResult], retrieve_precedent_hook(state, mock_deps))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_invalid_judge_output(mock_deps: HookDependencies) -> None:
    """Test Fail-Fast when TraceEvent output fails strict inflation to JudgeOutput."""
    from typing import cast

    cast(AsyncMock, mock_deps.repository.get_recent_completed_executions).return_value = [
        create_mock_execution(invalid_judge=True)
    ]
    state = HookState(
        execution_id="exe_current",
        workflow_id="wf_123",
        step_id="step_archivist",
        metadata={},
        global_context_vars={},
        inputs={},
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        from collections.abc import Awaitable
        from typing import cast

        from backend_v2.core.hook_registry import HookResult

        await cast(Awaitable[HookResult], retrieve_precedent_hook(state, mock_deps))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

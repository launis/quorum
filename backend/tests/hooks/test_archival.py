from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend.exceptions import AppException
from backend.hooks.archival import retrieve_precedent
from backend.models.domain.execution import ExecutionRecord
from backend.models.domain.judge import DimensionResultItem, JudgeOutput, JudgeScoreCard
from backend.models.state import TraceEvent, WorkflowState


@pytest.mark.asyncio
async def test_retrieve_precedent_no_repo():
    state = WorkflowState(workflow_id="test_workflow")
    state.context_variables["inputs"] = {}

    with pytest.raises(AppException) as excinfo:
        await retrieve_precedent(state, repository=None)

    assert "CONFIGURATION_ERROR" in str(excinfo.value.details)
    assert excinfo.value.status_code == 500


@pytest.mark.asyncio
async def test_retrieve_precedent_success():
    state = WorkflowState(workflow_id="current_workflow")
    state.context_variables["inputs"] = {}
    mock_repo = AsyncMock()

    judge_out = JudgeOutput(
        matrix_id="matrix_1",
        scale_min=0.0,
        scale_max=100.0,
        confidence_score=0.9,
        thought_process="Mock thought",
        conclusion="Mock conclusion",
        critical_findings=[],
        score_card=JudgeScoreCard(
            total_score=80.0,
            verdict="Verdict 1",
            agent_name="Standard",
            max_score=100,
            scale_min=0,
            scale_max=100,
            dimensions=[DimensionResultItem(dimension_id="dim1", dimension_label="Dim1", score=80.0, reasoning="OK")],
        ),
    )

    # Needs proper WorkflowState inside results
    past_state = WorkflowState(workflow_id="past")
    past_state = past_state.model_copy(
        update={
            "execution_trace": [TraceEvent(event_type="output", step_name="step_judge", content=judge_out.model_dump())]
        }
    )

    # Mock executions returning ExecutionRecord instances
    mock_repo.get_recent_completed_executions.return_value = [
        ExecutionRecord(
            id="exe-1",
            workflow_id="foo",
            status="completed",
            completed_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            results=past_state,
        )
    ]

    new_state = await retrieve_precedent(state, repository=mock_repo)

    assert "archivist_precedents" in new_state.context_variables
    summary = new_state.context_variables["archivist_precedents"]
    assert len(summary) > 0
    assert summary[0]["id"] == "exe-1"
    assert "Standard: 80.00" in summary[0]["scores"]


@pytest.mark.asyncio
async def test_retrieve_precedent_empty():
    state = WorkflowState(workflow_id="current_workflow")
    state.context_variables["inputs"] = {}
    mock_repo = AsyncMock()
    mock_repo.get_recent_completed_executions.return_value = []

    new_state = await retrieve_precedent(state, repository=mock_repo)

    assert "archivist_precedents" in new_state.context_variables
    summary = new_state.context_variables["archivist_precedents"]
    assert len(summary) == 0


@pytest.mark.asyncio
async def test_retrieve_precedent_integrity_error():
    state = WorkflowState(workflow_id="current_workflow")
    state.context_variables["inputs"] = {}
    mock_repo = AsyncMock()
    mock_repo.get_recent_completed_executions.return_value = [
        ExecutionRecord(
            id="exe-corrupt",
            workflow_id="foo",
            status="completed",
            completed_at=None,
        )
    ]

    with pytest.raises(AppException) as excinfo:
        await retrieve_precedent(state, repository=mock_repo)

    assert "STATE_INTEGRITY_ERROR" in str(excinfo.value.details)
    assert excinfo.value.status_code == 500


@pytest.mark.asyncio
async def test_retrieve_precedent_repo_error():
    state = WorkflowState(workflow_id="current_workflow")
    state.context_variables["inputs"] = {}
    mock_repo = AsyncMock()
    mock_repo.get_recent_completed_executions.side_effect = Exception("DB Down")

    with pytest.raises(AppException) as excinfo:
        await retrieve_precedent(state, repository=mock_repo)

    assert "KNOWLEDGE_RETRIEVAL_FAILED" in str(excinfo.value.details)
    assert "DB Down" in str(excinfo.value)

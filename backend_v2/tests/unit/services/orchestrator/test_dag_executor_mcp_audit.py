"""Unit tests for DAGExecutor MCP tool audit trace handling."""

import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionStatus,
    I18nText,
    MCPAuditTrace,
    StepRule,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "logic",
        "type": "logic",
        "model_strategy": "logic",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    repo.get_execution.return_value = None
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    return MagicMock()


@pytest.fixture
def workflow_fixture() -> Workflow:
    step = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    return Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wor_1111222233334444",
        slug="wf_mcp_audit_test",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(translations={"en": "MCP Audit Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step],
    )


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_trace_event_direct_accumulation(
    mock_repo: Any, mock_compiler: Any, workflow_fixture: Workflow
) -> None:
    """Tests that TraceEvents with mcp_audit_traces populated are merged into frozen_context."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    trace = MCPAuditTrace(
        id="tavily_001",
        tool_id="mcp_tavily_search",
        step_name="stp_1111222233334444",
        query="Verify quantum supremacy claim",
        reasoning="Fact check",
        response_summary="Google claimed supremacy in 2019",
        source_urls=["https://example.com/quantum"],
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        duration_ms=120,
    )

    trace_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="output",
        content={"result": "done"},
        mcp_audit_traces=[trace],
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        mock_node_execute.return_value = [trace_event]

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow_fixture,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

        assert record.status == ExecutionStatus.RUNNING
        assert len(record.frozen_context.mcp_tool_audit) == 1
        assert record.frozen_context.mcp_tool_audit[0].id == "tavily_001"
        assert record.frozen_context.mcp_tool_audit[0].source_urls == ["https://example.com/quantum"]


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_decision_event_merge_and_deduplication(
    mock_repo: Any, mock_compiler: Any, workflow_fixture: Workflow
) -> None:
    """Tests that raw dicts in decision event metadata are validated and deduplicated against existing traces."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    raw_trace1 = {
        "id": "tavily_dup_1",
        "tool_id": "mcp_tavily_search",
        "step_name": "stp_1111222233334444",
        "query": "Query 1",
        "reasoning": "Reasoning 1",
        "response_summary": "Summary 1",
        "source_urls": ["https://example.com/1"],
        "timestamp": now,
        "duration_ms": 100,
    }
    raw_trace2 = {
        "id": "tavily_dup_1",  # Same ID should be deduplicated
        "tool_id": "mcp_tavily_search",
        "step_name": "stp_1111222233334444",
        "query": "Query 1 duplicate",
        "reasoning": "Reasoning 1",
        "response_summary": "Summary 1",
        "source_urls": ["https://example.com/1"],
        "timestamp": now,
        "duration_ms": 100,
    }

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [raw_trace1, raw_trace2]},
        metadata={"mcp_audit_traces": [raw_trace1, raw_trace2]},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        mock_node_execute.return_value = [decision_event]

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow_fixture,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

        assert len(record.frozen_context.mcp_tool_audit) == 1
        assert record.frozen_context.mcp_tool_audit[0].id == "tavily_dup_1"


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_invalid_trace_fails_fast(
    mock_repo: Any, mock_compiler: Any, workflow_fixture: Workflow
) -> None:
    """Tests that a malformed raw dict in decision event metadata triggers Fail-Fast AppException."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    malformed_trace = {
        "id": "tavily_bad",
        # missing required tool_id, step_name, query, etc.
    }

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [malformed_trace]},
        metadata={"mcp_audit_traces": [malformed_trace]},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        mock_node_execute.return_value = [decision_event]

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow_fixture,
                raw_inputs=WorkflowInputs(dynamic_inputs={}),
            )

        assert exc_info.value.status_code == 500

"""Unit tests for DAGExecutor MCP tool audit trace handling."""

import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "logic",
        "type": "logic",
        "cognitive_tier": "fast",
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
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="cfg_model_registry_01",
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
    """Tests that typed MCPAuditTrace models in decision events are merged and deduplicated in frozen_context."""
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
    trace1 = MCPAuditTrace(
        id="tavily_dup_1",
        tool_id="mcp_tavily_search",
        step_name="stp_1111222233334444",
        query="Query 1",
        reasoning="Reasoning 1",
        response_summary="Summary 1",
        source_urls=["https://example.com/1"],
        timestamp=now,
        duration_ms=100,
    )
    trace2 = MCPAuditTrace(
        id="tavily_dup_1",  # Same ID should be deduplicated
        tool_id="mcp_tavily_search",
        step_name="stp_1111222233334444",
        query="Query 1 duplicate",
        reasoning="Reasoning 1",
        response_summary="Summary 1",
        source_urls=["https://example.com/1"],
        timestamp=now,
        duration_ms=100,
    )

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [trace1.model_dump(mode="json"), trace2.model_dump(mode="json")]},
        metadata={"mcp_audit_traces": [trace1.model_dump(mode="json"), trace2.model_dump(mode="json")]},
        mcp_audit_traces=[trace1, trace2],
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


def test_dag_executor_mcp_audit_invalid_trace_fails_fast() -> None:
    """Tests that a malformed raw dict passed to TraceEvent mcp_audit_traces triggers Fail-Fast ValidationError."""
    import pydantic

    malformed_trace = {
        "id": "tavily_bad",
        # missing required tool_id, step_name, query
    }

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TraceEvent(
            step_name="stp_1111222233334444",
            event_type="decision",
            content={"mcp_audit_traces": [malformed_trace]},
            metadata={"mcp_audit_traces": [malformed_trace]},
            mcp_audit_traces=[malformed_trace],  # type: ignore[list-item]
        )

    assert "tool_id" in str(exc_info.value) or "Input should be a valid dictionary or instance of MCPAuditTrace" in str(exc_info.value)


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_decision_event_with_iso_string_timestamp(
    mock_repo: Any, mock_compiler: Any, workflow_fixture: Workflow
) -> None:
    """Regression test: verify MCPAuditTrace hydrated from serialized data flows through TraceEvent into frozen_context."""
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

    raw_trace_iso = {
        "id": "tavily_iso_001",
        "tool_id": "mcp_tavily_search",
        "step_name": "stp_1111222233334444",
        "query": "Verify fact check",
        "reasoning": "Reasoning text",
        "response_summary": "Extracted summary",
        "source_urls": ["https://example.com/source"],
        "timestamp": "2026-09-23T14:43:20.852846Z",
        "duration_ms": 125,
    }

    # Hydrated with strict=False at the reconstitution boundary
    trace = MCPAuditTrace.model_validate(raw_trace_iso, strict=False)

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [raw_trace_iso]},
        metadata={"mcp_audit_traces": [raw_trace_iso]},
        mcp_audit_traces=[trace],
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

        assert record.status == ExecutionStatus.RUNNING
        assert len(record.frozen_context.mcp_tool_audit) == 1
        audit_entry = record.frozen_context.mcp_tool_audit[0]
        assert audit_entry.id == "tavily_iso_001"
        assert isinstance(audit_entry.timestamp, datetime.datetime)


def test_mcp_audit_trace_istqb_negative_boundary_partitions() -> None:
    """ISTQB Negative Boundary Test Partitions for MCPAuditTrace and TraceEvent ingress contracts."""
    import pydantic

    # Partition Neg-1: Malformed dictionary in TraceEvent(mcp_audit_traces=[...]) fails fast with ValidationError
    with pytest.raises(pydantic.ValidationError) as exc_neg1:
        TraceEvent(
            step_name="stp_1111222233334444",
            event_type="decision",
            mcp_audit_traces=[{"invalid_field": 123}],  # type: ignore[list-item]
        )
    assert "tool_id" in str(exc_neg1.value) or "Input should be a valid dictionary or instance of MCPAuditTrace" in str(exc_neg1.value)

    # Partition Neg-2: Attempting to instantiate MCPAuditTrace without mandatory fields fails fast
    with pytest.raises(pydantic.ValidationError) as exc_neg2:
        MCPAuditTrace.model_validate({"id": "tavily_bad"})
    assert "tool_id" in str(exc_neg2.value)
    assert "step_name" in str(exc_neg2.value)
    assert "query" in str(exc_neg2.value)

    # Partition Neg-3: Passing string timestamp into MCPAuditTrace.model_validate(raw, strict=True)
    # raises ValidationError, mathematically proving why the producer MUST pass native datetime or typed instances
    raw_with_str_timestamp = {
        "tool_id": "mcp_search",
        "step_name": "stp_step_1",
        "query": "claim check",
        "timestamp": "2026-09-23T14:43:20.852846Z",
    }
    with pytest.raises(pydantic.ValidationError) as exc_neg3:
        MCPAuditTrace.model_validate(raw_with_str_timestamp, strict=True)
    assert "Input should be a valid datetime" in str(exc_neg3.value)


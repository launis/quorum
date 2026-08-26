"""Unit tests for DAGExecutor parallel execution, atomic MCP audit deduplication, and schema accumulation."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    I18nText,
    MCPAuditTrace,
    StepRule,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repos() -> dict[str, Any]:
    exec_repo = AsyncMock()
    exec_repo.get_execution = AsyncMock(return_value=None)
    exec_repo.create_execution = AsyncMock(side_effect=lambda rec: rec)
    exec_repo.update_execution = AsyncMock()

    workflow_repo = AsyncMock()
    workflow_repo.get_step_by_id = AsyncMock(
        side_effect=lambda bp_id: {
            "id": bp_id,
            "type": "logic",
            "model_strategy": "logic",
            "slug": f"slug_{bp_id}",
            "name": {"translations": {"en": f"Step {bp_id}"}},
            "description": {"translations": {"en": "Desc"}},
            "hook": "mock_hook",
            "criteria_block_ids": [],
        }
    )
    workflow_repo.get_workflow_by_id = AsyncMock(
        side_effect=lambda wf_id: {
            "id": wf_id,
            "slug": f"slug_{wf_id}",
            "name": {"translations": {"en": "Workflow"}},
            "description": {"translations": {"en": "Desc"}},
            "version": 1,
            "status": "active",
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "steps": [],
        }
    )

    return {
        "exec_repo": exec_repo,
        "workflow_repo": workflow_repo,
        "comp_repo": AsyncMock(),
        "prompt_block_repo": AsyncMock(),
        "output_profile_repo": AsyncMock(),
        "identity_repo": AsyncMock(),
        "audit_repo": AsyncMock(),
        "system_repo": AsyncMock(),
        "prompt_compiler": MagicMock(),
        "rag_preflight": AsyncMock(),
    }


@pytest.mark.asyncio
async def test_dag_executor_mcp_concurrency_deduplication(mock_repos: dict[str, Any]) -> None:
    """Verify that concurrent steps emitting MCPAuditTrace with overlapping IDs are atomically deduplicated."""
    executor = DAGExecutor(
        exec_repo=mock_repos["exec_repo"],
        workflow_repo=mock_repos["workflow_repo"],
        comp_repo=mock_repos["comp_repo"],
        prompt_block_repo=mock_repos["prompt_block_repo"],
        output_profile_repo=mock_repos["output_profile_repo"],
        identity_repo=mock_repos["identity_repo"],
        audit_repo=mock_repos["audit_repo"],
        system_repo=mock_repos["system_repo"],
        prompt_compiler=mock_repos["prompt_compiler"],
        rag_preflight=mock_repos["rag_preflight"],
    )

    # 3 parallel steps without dependencies
    steps = [
        StepRule(id="stp_aaaaaaaaaaaaaaaa", task_blueprint="bp_aaaaaaaaaaaaaaaa", depends_on=[]),
        StepRule(id="stp_bbbbbbbbbbbbbbbb", task_blueprint="bp_bbbbbbbbbbbbbbbb", depends_on=[]),
        StepRule(id="stp_cccccccccccccccc", task_blueprint="bp_cccccccccccccccc", depends_on=[]),
    ]

    workflow = Workflow(
        id="wf_1111111111111111",
        slug="wf_concurrency_1",
        name=I18nText(translations={"en": "Concurrency Test"}),
        description=I18nText(translations={"en": "Concurrency Test"}),
        version=1,
        status="active",
        default_profile_id="prof_1111111111111111",
        allowed_exports=["pdf"],
        historical_context_mode="DISABLED",
        steps=steps,
    )

    # Step A emits trace_1 and trace_2
    trace_1 = MCPAuditTrace(
        id="mcp_trace_1",
        tool_id="web_search",
        step_name="stp_aaaaaaaaaaaaaaaa",
        query="test 1",
        response_summary="found 1",
    )
    trace_2 = MCPAuditTrace(
        id="mcp_trace_2",
        tool_id="doc_fetch",
        step_name="stp_aaaaaaaaaaaaaaaa",
        query="doc_1",
        response_summary="data 1",
    )

    # Step B emits duplicate trace_1 and new trace_3
    trace_3 = MCPAuditTrace(
        id="mcp_trace_3",
        tool_id="web_search",
        step_name="stp_bbbbbbbbbbbbbbbb",
        query="test 3",
        response_summary="found 3",
    )

    # Step C emits duplicate trace_2
    async def mock_execute_node(step: StepRule, **kwargs: Any) -> list[TraceEvent]:
        await asyncio.sleep(0.01)  # Yield to maximize concurrency interleaving
        if step.id == "stp_aaaaaaaaaaaaaaaa":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content={"data": "A"},
                    mcp_audit_traces=[trace_1, trace_2],
                )
            ]
        elif step.id == "stp_bbbbbbbbbbbbbbbb":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content={"data": "B"},
                    mcp_audit_traces=[trace_1, trace_3],
                )
            ]
        else:
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content={"data": "C"},
                    mcp_audit_traces=[trace_2],
                )
            ]

    with patch.object(executor.node_executor, "execute", side_effect=mock_execute_node):
        record = await executor.execute_workflow(
            execution_id="exe_1111111111111111",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "hello"}, language="en"),
        )

    # Verify that all 3 unique MCP traces are present without duplicates
    mcp_audits = record.frozen_context.mcp_tool_audit
    mcp_ids = [t.id for t in mcp_audits]
    assert len(mcp_ids) == 3
    assert set(mcp_ids) == {"mcp_trace_1", "mcp_trace_2", "mcp_trace_3"}


@pytest.mark.asyncio
async def test_dag_executor_generated_schemas_accumulation(mock_repos: dict[str, Any]) -> None:
    """Verify that concurrent steps emitting generated_schema in metadata are accumulated in frozen_context."""
    executor = DAGExecutor(
        exec_repo=mock_repos["exec_repo"],
        workflow_repo=mock_repos["workflow_repo"],
        comp_repo=mock_repos["comp_repo"],
        prompt_block_repo=mock_repos["prompt_block_repo"],
        output_profile_repo=mock_repos["output_profile_repo"],
        identity_repo=mock_repos["identity_repo"],
        audit_repo=mock_repos["audit_repo"],
        system_repo=mock_repos["system_repo"],
        prompt_compiler=mock_repos["prompt_compiler"],
        rag_preflight=mock_repos["rag_preflight"],
    )

    steps = [
        StepRule(id="stp_1111111111111111", task_blueprint="bp_1111111111111111", depends_on=[]),
        StepRule(id="stp_2222222222222222", task_blueprint="bp_2222222222222222", depends_on=[]),
    ]

    workflow = Workflow(
        id="wf_2222222222222222",
        slug="wf_concurrency_2",
        name=I18nText(translations={"en": "Schema Test"}),
        description=I18nText(translations={"en": "Schema Test"}),
        version=1,
        status="active",
        default_profile_id="prof_1111111111111111",
        allowed_exports=["pdf"],
        historical_context_mode="DISABLED",
        steps=steps,
    )

    schema_x = {"type": "object", "properties": {"x": {"type": "string"}}}
    schema_y = {"type": "object", "properties": {"y": {"type": "integer"}}}

    async def mock_execute_node(step: StepRule, **kwargs: Any) -> list[TraceEvent]:
        await asyncio.sleep(0.01)
        schema = schema_x if step.id == "stp_1111111111111111" else schema_y
        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content={"data": step.id},
                metadata={"generated_schema": schema},
            )
        ]

    with patch.object(executor.node_executor, "execute", side_effect=mock_execute_node):
        record = await executor.execute_workflow(
            execution_id="exe_2222222222222222",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "hello"}, language="en"),
        )

    # Verify that generated_schemas contains schemas for both steps
    schemas = record.frozen_context.generated_schemas
    assert "stp_1111111111111111" in schemas
    assert schemas["stp_1111111111111111"] == schema_x
    assert "stp_2222222222222222" in schemas
    assert schemas["stp_2222222222222222"] == schema_y

import asyncio
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.enums import HistoricalContextMode
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
def mock_dag_executor_deps() -> dict[str, Any]:
    mock_repo = AsyncMock()
    mock_compiler = MagicMock()
    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.side_effect = lambda b_id: {
        "id": b_id,
        "slug": f"slug_{b_id}",
        "name": {"default_locale": "en", "translations": {"en": b_id}},
        "type": "logic",
        "hook": "mock_hook",
    }
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    return {
        "executor": executor,
        "repo": mock_repo,
        "workflow_repo": mock_workflow_repo,
        "compiler": mock_compiler,
    }


def _create_test_workflow(step_rules: list[StepRule]) -> Workflow:
    return Workflow(
        id="wor_1111222233334444",
        slug="wor_test_mcp_concurrency",
        name=I18nText(default_locale="en", translations={"en": "MCP Concurrency WF"}),
        description=I18nText(default_locale="en", translations={"en": "Test WF"}),
        status="draft",
        version=1,
        default_profile_id="prf_1111222233334444",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=step_rules,
    )


@pytest.mark.asyncio
async def test_dag_executor_concurrent_steps_accumulate_mcp_traces(mock_dag_executor_deps: dict[str, Any]) -> None:
    """TC-MCP-01: Multi-step accumulation preserves all unique MCP audit traces across parallel steps."""
    executor: DAGExecutor = mock_dag_executor_deps["executor"]
    mock_repo: AsyncMock = mock_dag_executor_deps["repo"]

    # 4 parallel steps with no dependencies between each other
    steps = [
        StepRule(id="stp_1111000000000001", task_blueprint="blp_1111000000000001", depends_on=[]),
        StepRule(id="stp_1111000000000002", task_blueprint="blp_1111000000000002", depends_on=[]),
        StepRule(id="stp_1111000000000003", task_blueprint="blp_1111000000000003", depends_on=[]),
        StepRule(id="stp_1111000000000004", task_blueprint="blp_1111000000000004", depends_on=[]),
    ]
    workflow = _create_test_workflow(steps)

    mock_repo.get_execution.return_value = None
    mock_repo.get_user = AsyncMock(return_value={"language": "en"})

    async def mock_node_execute(**kwargs: Any) -> list[TraceEvent]:
        step_rule = kwargs["step"]
        step_id = step_rule.id
        await asyncio.sleep(0.01)
        return [
            TraceEvent(
                event_id=uuid.uuid4(),
                step_name=step_id,
                event_type="decision",
                content={"result": f"{step_id}_done"},
                mcp_audit_traces=[
                    MCPAuditTrace(
                        id=f"mcp_{step_id}_1",
                        tool_id="mcp_tavily_search",
                        step_name=step_id,
                        query=f"query 1 from {step_id}",
                    ),
                    MCPAuditTrace(
                        id=f"mcp_{step_id}_2",
                        tool_id="mcp_tavily_search",
                        step_name=step_id,
                        query=f"query 2 from {step_id}",
                    ),
                ],
            )
        ]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"text": "test document"}})
        )
        mock_execute.side_effect = mock_node_execute

        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "test"}, language="en"),
        )

    # Inspect committed records
    committed_frozen = [
        call.args[1]["frozen_context"]
        for call in mock_repo.update_execution.call_args_list
        if len(call.args) > 1 and "frozen_context" in call.args[1]
    ]
    assert len(committed_frozen) > 0
    final_frozen_dict = committed_frozen[-1]

    trace_ids = {t["id"] for t in final_frozen_dict.get("mcp_tool_audit", [])}
    expected_ids = {
        "mcp_stp_1111000000000001_1",
        "mcp_stp_1111000000000001_2",
        "mcp_stp_1111000000000002_1",
        "mcp_stp_1111000000000002_2",
        "mcp_stp_1111000000000003_1",
        "mcp_stp_1111000000000003_2",
        "mcp_stp_1111000000000004_1",
        "mcp_stp_1111000000000004_2",
    }
    assert trace_ids == expected_ids
    assert len(final_frozen_dict.get("mcp_tool_audit", [])) == 8


@pytest.mark.asyncio
async def test_dag_executor_mcp_trace_deduplication(mock_dag_executor_deps: dict[str, Any]) -> None:
    """TC-MCP-02: Duplicate trace IDs across concurrent steps are safely deduplicated."""
    executor: DAGExecutor = mock_dag_executor_deps["executor"]
    mock_repo: AsyncMock = mock_dag_executor_deps["repo"]

    steps = [
        StepRule(id="stp_1111000000000001", task_blueprint="blp_1111000000000001", depends_on=[]),
        StepRule(id="stp_1111000000000002", task_blueprint="blp_1111000000000002", depends_on=[]),
    ]
    workflow = _create_test_workflow(steps)

    mock_repo.get_execution.return_value = None
    mock_repo.get_user = AsyncMock(return_value={"language": "en"})

    async def mock_node_execute(**kwargs: Any) -> list[TraceEvent]:
        step_rule = kwargs["step"]
        step_id = step_rule.id
        return [
            TraceEvent(
                event_id=uuid.uuid4(),
                step_name=step_id,
                event_type="decision",
                content={"result": "done"},
                mcp_audit_traces=[
                    # Duplicate shared trace ID
                    MCPAuditTrace(
                        id="mcp_shared_001",
                        tool_id="mcp_tavily_search",
                        step_name=step_id,
                        query="shared duplicate query",
                    ),
                    # Unique trace
                    MCPAuditTrace(
                        id=f"mcp_unique_{step_id}",
                        tool_id="mcp_tavily_search",
                        step_name=step_id,
                        query=f"unique query from {step_id}",
                    ),
                ],
            )
        ]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"text": "test document"}})
        )
        mock_execute.side_effect = mock_node_execute

        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "test"}, language="en"),
        )

    committed_frozen = [
        call.args[1]["frozen_context"]
        for call in mock_repo.update_execution.call_args_list
        if len(call.args) > 1 and "frozen_context" in call.args[1]
    ]
    assert len(committed_frozen) > 0
    final_frozen_dict = committed_frozen[-1]

    trace_ids = [t["id"] for t in final_frozen_dict.get("mcp_tool_audit", [])]
    assert trace_ids.count("mcp_shared_001") == 1
    assert "mcp_unique_stp_1111000000000001" in trace_ids
    assert "mcp_unique_stp_1111000000000002" in trace_ids
    assert len(final_frozen_dict.get("mcp_tool_audit", [])) == 3


@pytest.mark.asyncio
async def test_dag_executor_frozen_context_immutability_and_commit(mock_dag_executor_deps: dict[str, Any]) -> None:
    """TC-MCP-03: Immutability is preserved and commit_trace persists accumulated MCPAuditTrace."""
    executor: DAGExecutor = mock_dag_executor_deps["executor"]
    mock_repo: AsyncMock = mock_dag_executor_deps["repo"]

    steps = [
        StepRule(id="stp_1111000000000001", task_blueprint="blp_1111000000000001", depends_on=[]),
    ]
    workflow = _create_test_workflow(steps)

    mock_repo.get_execution.return_value = None
    mock_repo.get_user = AsyncMock(return_value={"language": "en"})

    mock_trace = MCPAuditTrace(
        id="mcp_test_001",
        tool_id="mcp_tavily_search",
        step_name="stp_1111000000000001",
        query="test search query",
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"text": "test document"}})
        )
        mock_execute.return_value = [
            TraceEvent(
                event_id=uuid.uuid4(),
                step_name="stp_1111000000000001",
                event_type="decision",
                content={"result": "ok"},
                mcp_audit_traces=[mock_trace],
            )
        ]

        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "test"}, language="en"),
        )

    committed_frozen = [
        call.args[1]["frozen_context"]
        for call in mock_repo.update_execution.call_args_list
        if len(call.args) > 1 and "frozen_context" in call.args[1]
    ]
    assert len(committed_frozen) > 0
    final_frozen_dict = committed_frozen[-1]

    mcp_audits = final_frozen_dict.get("mcp_tool_audit", [])
    assert len(mcp_audits) == 1
    assert mcp_audits[0]["id"] == "mcp_test_001"
    assert mcp_audits[0]["query"] == "test search query"

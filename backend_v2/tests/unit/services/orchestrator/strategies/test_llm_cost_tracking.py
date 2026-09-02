"""Reproduction unit test for TDA Engine & LLM Strategy Cost / Token Usage Tracking.

Proves that TDAEngine and LLMStrategy currently fail to aggregate and propagate
TokenUsage and cost_usd from internal LLM executions into TraceEvent._step_metadata.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import GlobalOntologyMap
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.strategies.base import StrategyContext
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_step_by_id = AsyncMock()
    repo.get_all_prompt_blocks = AsyncMock(return_value=[])
    repo.get_output_profile_by_id = AsyncMock(
        return_value={
            "id": "prof_0123456789abcdef0123456789abcdef",
            "slug": "test",
            "name": {"translations": {"en": "Test"}},
            "workflow_id": "wf_123",
            "organization_id": "root",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_1234567890123456",
                    "title": {"translations": {"en": "Test"}},
                    "target_blocks": ["*"],
                }
            ],
        }
    )
    repo.get_workflow = AsyncMock(
        return_value={
            "id": "wf_0123456789abcdef0123456789abcdef",
            "slug": "test",
            "name": {"translations": {"en": "Test"}},
            "description": {"translations": {"en": "Test"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "steps": [],
        }
    )
    repo.get_execution = AsyncMock(return_value=None)
    return repo


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
async def test_tda_engine_aggregates_token_usage_and_cost(
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    mock_compiler: MagicMock,
) -> None:
    """Reproduction Test 1: TDAEngine MUST return aggregated TokenUsage including cost_usd."""
    from backend_v2.llm.client import LLMClient
    from backend_v2.models.dtos.engine import FlattenedAtom

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    mock_atomizer_instance.execute_phase_0 = AsyncMock(
        return_value=(
            GlobalOntologyMap(entities=[], macro_rules=[]),
            TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120, cost_usd=0.005),
        )
    )
    mock_dag_executor_instance.execute_graph = AsyncMock(
        return_value=(
            {},
            TokenUsage(prompt_tokens=300, completion_tokens=60, total_tokens=360, cost_usd=0.015),
        )
    )
    mock_projector.project.return_value = ([], {})

    shuffled_atom = FlattenedAtom(
        atom_id="tda_12345678",
        question="Is this claim valid?",
        extraction_rule="Test rule",
        anchor_target="target_1",
        is_inverse=False,
        depends_on=(),
    )

    engine_request = EngineExecutionRequest(
        bound_client=MagicMock(spec=LLMClient),
        compiled_schema=None,
        hydrated_messages=None,
        system_prompt="Test System Prompt",
        step=StepRule(id="step_a1b2c3d4e5f6a7b8", task_blueprint="task_123", depends_on=[], input_mappings={}),
        context=StrategyContext(
            execution_id="exe_abc12345",
            workflow_id="wor_xyz12345",
            metadata=ExecutionMetadata(),
        ),
        global_source_text="Test source text",
        target_locale="fi",
        semaphore=asyncio.Semaphore(1),
        running_event=asyncio.Event(),
        progress_callback=AsyncMock(),
        trace_callback=AsyncMock(),
        prompt_compiler=mock_compiler,
        shuffled_atoms=[shuffled_atom],
    )

    from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(engine_request)

    assert isinstance(result, EngineExecutionResult)
    # The result MUST carry the aggregated usage
    assert result.usage is not None
    assert result.usage.total_tokens == (120 + 360)
    assert abs(result.usage.cost_usd - (0.005 + 0.015)) < 1e-6


@pytest.mark.asyncio
async def test_llm_strategy_propagates_engine_usage_to_trace_event(
    mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Reproduction Test 2: LLMStrategy MUST propagate EngineExecutionResult.usage to TraceEvent._step_metadata."""
    mock_engine = MagicMock()
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    llm_strategy = LLMNodeStrategy(deps=deps, engine=mock_engine)

    step = MagicMock()
    step.id = "step_test_cost"
    step.task_blueprint = "bp_cost"
    step.input_mappings = {"$test": "path.to.test"}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = ExecutionMetadata()
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Test", "fi": "Test"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": ["blk_0123456789abcdef0123456789abcdef"],
        "model_strategy": "standard",
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_0123456789abcdef0123456789abcdef",
            "slug": "test_block",
            "category_id": "system_rule",
            "type": "string",
            "label": {"translations": {"en": "Label", "fi": "Label"}},
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "instruction_text": "Test Block AI Desc",
        },
        {
            "id": "blk_573802341db9d68c",
            "slug": "zero_trust_extraction_protocol",
            "category_id": "system_rule",
            "type": "instruction",
            "label": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "description": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "instruction_text": "Strict extraction protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"path": {"to": {"test": "value"}}}
    mock_hook_state.global_context_vars = {}

    expected_usage = TokenUsage(
        prompt_tokens=500,
        completion_tokens=100,
        total_tokens=600,
        cost_usd=0.025,
    )

    mock_engine.execute = AsyncMock(
        return_value=EngineExecutionResult(
            results=[],
            hydrated_references={},
            usage=expected_usage,
        )
    )

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"blocks": []}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    trace_event = traces[0]
    assert trace_event.event_type == "output"
    assert "_step_metadata" in trace_event.content
    step_meta = trace_event.content["_step_metadata"]
    assert "token_usage" in step_meta
    assert step_meta["token_usage"]["total_tokens"] == 600
    assert step_meta["token_usage"]["cost_usd"] == 0.025

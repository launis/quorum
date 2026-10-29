"""Unit tests for Stage 3 LLMClient binding, MCP tool retrieval, and bounded engine retry loop."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import ExecutionInputsDTO, GlobalContextVarsDTO, HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.mcp import MCPRetrievalResultDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.engine import EngineExecutionResult
from backend_v2.models.dtos.prompt import PromptMappingDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EngineType,
    ExecutionStatus,
    PromptBlockCategory,
    StepType,
    StepZone,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptPayload
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage import (
    EngineRetryStageResult,
    execute_engine_retry_stage,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.utils.alias_engine import AliasEngine


class _SampleSynthesisModel(BaseModel):
    """Strict sample Pydantic model for synthesis_output normalization testing."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    summary_title: str
    optional_note: str | None = None


def _create_rule_block(block_id: str = "blk_0195f3a0000070008123456789abcdef") -> SystemRulePromptBlock:
    """Create a valid SystemRulePromptBlock for Stage 3 testing."""
    return SystemRulePromptBlock(
        id=block_id,
        slug="rule-blk",
        label=I18nText(translations={"en": "Rule", "fi": "Saanto"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        instruction_text="Evaluate carefully.",
    )


def _create_matrix_block(block_id: str = "blk_0195f3a0000070058555555555555555") -> MatrixPromptBlock:
    """Create a valid MatrixPromptBlock for Stage 3 testing."""
    from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion

    assertion = TDAAssertion(
        tda_id="tda_0123456789abcdef0123456789abcdef",
        concept_description="Verify clear structure.",
        aggregation_mode="EXISTS",
        inverse_evidence=False,
        depends_on=(),
    )
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Claim 1", "fi": "Vaite 1"}),
        tda_assertions=[assertion],
    )
    return MatrixPromptBlock(
        id=block_id,
        slug="matrix-blk",
        label=I18nText(translations={"en": "Matrix", "fi": "Matriisi"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        ai_description="Evaluate against matrix.",
        allow_contextual_override=True,
        scales=[
            MatrixScale(score=1, ai_label="Novice", claims=[claim]),
            MatrixScale(score=5, ai_label="Expert", claims=[claim]),
        ],
    )


def _build_stage1_and_stage2(
    *,
    repo: InMemoryUnifiedWorkflowRepository,
    criteria_blocks: list[PromptBlock],
    allowed_mcp_tools: list[str] | None = None,
    user_payload: str = "Compiled user payload.",
    global_source_text: str = "Primary source document text.",
) -> tuple[BlueprintStageResult, PromptAndSchemaStageResult]:
    """Construct paired Stage 1 and Stage 2 containers for Stage 3 unit testing."""
    proto_blk = ProtocolPromptBlock(
        id="blk_0195f3a00000700a8000000000000002",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol", "fi": "Protokolla"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract exact quotes.",
    )
    step_obj = Step(
        id="stp_0195f3a0000070008123456789abcdef",
        slug="test-step",
        name=I18nText(translations={"en": "Test Step", "fi": "Testivaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        extraction_protocol_block_id=proto_blk.id,
        criteria_block_ids=[b.id for b in criteria_blocks],
        allowed_mcp_tools=allowed_mcp_tools if allowed_mcp_tools is not None else [],
        mcp_tool_params={},
        is_system_core=False,
    )
    profile = OutputProfile(
        id="prf_0195f3a0000070008123456789abcdef",
        slug="default-prf",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        name=I18nText(translations={"en": "Default"}),
        target_block_order=[],
    )
    inputs_dto = ExecutionInputsDTO(
        raw_inputs={"doc": global_source_text},
        dynamic_inputs={"doc": global_source_text},
        target_locale="en",
    )
    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint=step_obj.id,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs_dto,
    )
    stage1 = BlueprintStageResult(
        step_obj=step_obj,
        workflow_obj=None,
        hook_state=hook_state,
        hook_deps=HookDependencies(
            exec_repo=repo,
            workflow_repo=repo,
            comp_repo=repo,
            prompt_block_repo=repo,
            output_profile_repo=repo,
            identity_repo=repo,
            audit_repo=repo,
            system_repo=repo,
        ),
        pre_events=[],
        block_map={b.id: b for b in [*criteria_blocks, proto_blk]},
        role_block=None,
        protocol_block=proto_blk,
        execution_persona_block=None,
        criteria_blocks_models=criteria_blocks,
        output_profile_id=profile.id,
        output_profile=profile,
        target_locale="en",
        global_source_text=global_source_text,
        state_data={"inputs": {"doc": global_source_text}},
        inputs_payload=inputs_dto,
    )
    matrix_blk = next((b for b in criteria_blocks if isinstance(b, MatrixPromptBlock)), None)
    stage2 = PromptAndSchemaStageResult(
        hook_state=hook_state,
        criteria_blocks=criteria_blocks,
        matrix_block=matrix_blk,
        hydrated_shuffled_atoms=None,
        alias_engine=AliasEngine(),
        prompt_payload=PromptPayload(
            base_system_prompt="Static base prompt.",
            user_payload=user_payload,
            atom_to_block_ids={},
        ),
        user_payload=user_payload,
        target_chunks=[["chunk_0"]],
        dynamic_schema=None,
        is_synthesis_step=False,
        source_doc_ctx=[],
        input_mappings=PromptMappingDTO(mappings={}),
        schema_map={},
        blueprint_labels={},
    )
    return stage1, stage2


def _create_ctx(cognitive_tier: CognitiveTier | None = CognitiveTier.FAST) -> StrategyContext:
    """Create a StrategyContext for Stage 3 testing."""
    if cognitive_tier is None:
        raw_none_tier: Any = None
        return StrategyContext.model_construct(
            execution_id="exe_0195f3a0000070008123456789abcdef",
            workflow_id="wf_0195f3a0000070008123456789abcdef",
            output_profile_id="prf_0195f3a0000070008123456789abcdef",
            target_locale="en",
            cognitive_tier=raw_none_tier,
            metadata=ExecutionMetadata(),
            global_context_vars=GlobalContextVarsDTO(),
            context_variables=ContextVariablesDTO(),
            prompt_blocks=[],
            expected_inputs=[],
            strictness_level=100,
            model_registry_id=None,
        )
    return StrategyContext(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        output_profile_id="prf_0195f3a0000070008123456789abcdef",
        target_locale="en",
        cognitive_tier=cognitive_tier,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        context_variables=ContextVariablesDTO(),
        prompt_blocks=[],
        expected_inputs=[],
    )


@pytest.fixture
def in_memory_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a stateful in-memory repository with an active ExecutionRecord."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.set_execution(
        ExecutionRecord(
            id="exe_0195f3a0000070008123456789abcdef",
            workflow_id="wf_0195f3a0000070008123456789abcdef",
            output_profile_id="prf_0195f3a0000070008123456789abcdef",
            target_locale="en",
            status=ExecutionStatus.RUNNING,
            metadata=ExecutionMetadata(),
            step_states={
                "sr_0195f3a0000070008123456789abcdef": ExecutionStepState(
                    id="sr_0195f3a0000070008123456789abcdef",
                    label="Test Step",
                    status=ExecutionStatus.RUNNING,
                )
            },
        )
    )
    return repo


@pytest.fixture
def strategy_deps(in_memory_repo: InMemoryUnifiedWorkflowRepository) -> StrategyDependencies:
    """Provide StrategyDependencies wired to the stateful in-memory repository."""
    return StrategyDependencies(
        exec_repo=in_memory_repo,
        workflow_repo=in_memory_repo,
        comp_repo=in_memory_repo,
        prompt_block_repo=in_memory_repo,
        output_profile_repo=in_memory_repo,
        identity_repo=in_memory_repo,
        audit_repo=in_memory_repo,
        system_repo=in_memory_repo,
        prompt_compiler=PromptCompiler(),
    )


@pytest.mark.asyncio
async def test_execute_anomaly_retry_flow(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_engine_retry_stage retries on llm_anomaly_retry_requested and updates step_states in DB."""
    rule_block = _create_rule_block()
    stage1, stage2 = _build_stage1_and_stage2(repo=in_memory_repo, criteria_blocks=[rule_block])
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )
    ctx = _create_ctx()

    mock_engine = MagicMock()
    mock_engine.execute = AsyncMock(
        side_effect=[
            EngineExecutionResult(
                results=[],
                hydrated_references={},
                synthesis_output=_SampleSynthesisModel(summary_title="First Attempt"),
                usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            ),
            EngineExecutionResult(
                results=[],
                hydrated_references={},
                synthesis_output=_SampleSynthesisModel(summary_title="Second Attempt Resolved"),
                usage=TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            ),
        ]
    )

    call_idx = 0

    async def _post_hooks_retry_once(
        *,
        step_obj: Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        nonlocal call_idx
        call_idx += 1
        if call_idx == 1:
            retry_state = hook_state.model_copy(
                update={
                    "inputs": ExecutionInputsDTO(
                        dynamic_inputs={"llm_anomaly_retry_requested": True, "summary_title": "First Attempt"}
                    )
                }
            )
            return retry_state, []
        resolved_state = hook_state.model_copy(
            update={"inputs": ExecutionInputsDTO(dynamic_inputs={"summary_title": "Second Attempt Resolved"})}
        )
        return resolved_state, [TraceEvent(step_name=step.id, event_type="decision", content={"ok": True})]

    mock_settings = MagicMock()
    mock_settings.llm_max_retries = 2
    mock_client = MagicMock(spec=LLMClient)
    mock_client.model_name = "gpt-4o"
    with patch(
        "backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage.LLMClient.from_tier",
        new=AsyncMock(return_value=mock_client),
    ):
        result = await execute_engine_retry_stage(
            stage1=stage1,
            stage2=stage2,
            step=step,
            context=ctx,
            deps=strategy_deps,
            engine=mock_engine,
            run_post_hooks_fn=_post_hooks_retry_once,
            settings_getter=lambda: mock_settings,
        )

    assert isinstance(result, EngineRetryStageResult)
    assert mock_engine.execute.await_count == 2
    assert result.final_dict["summary_title"] == "Second Attempt Resolved"
    assert "llm_anomaly_retry_requested" not in result.final_dict
    assert len(result.post_events) == 1
    assert result.usage_agg.total_tokens == 30

    # Verify stateful roundtrip persistence on ExecutionRecord.step_states
    persisted_exec = await in_memory_repo.get_execution("exe_0195f3a0000070008123456789abcdef")
    assert persisted_exec is not None
    assert persisted_exec.step_states["sr_0195f3a0000070008123456789abcdef"].status == ExecutionStatus.RUNNING
    assert persisted_exec.step_states["sr_0195f3a0000070008123456789abcdef"].message_code == "event_llm_anomaly_retry"


@pytest.mark.asyncio
async def test_execute_fails_fast_when_no_engine_configured(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_engine_retry_stage raises ConfigurationError when engine=None or cognitive_tier is missing."""
    rule_block = _create_rule_block()
    stage1, stage2 = _build_stage1_and_stage2(repo=in_memory_repo, criteria_blocks=[rule_block])
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )

    # 1. Missing cognitive_tier fails fast before LLMClient.from_tier
    ctx_no_tier = _create_ctx(cognitive_tier=None)
    with pytest.raises(AppException, match="has no cognitive_tier defined") as exc_no_tier:
        await execute_engine_retry_stage(
            stage1=stage1,
            stage2=stage2,
            step=step,
            context=ctx_no_tier,
            deps=strategy_deps,
            engine=MagicMock(),
            run_post_hooks_fn=AsyncMock(),
        )
    assert exc_no_tier.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    # 2. Missing engine=None fails fast with CONFIGURATION_ERROR
    ctx = _create_ctx()
    with patch(
        "backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage.LLMClient.from_tier",
        new=AsyncMock(return_value=MagicMock()),
    ):
        with pytest.raises(AppException, match="LLMNodeStrategy has no ExecutionEngine configured") as exc_no_engine:
            await execute_engine_retry_stage(
                stage1=stage1,
                stage2=stage2,
                step=step,
                context=ctx,
                deps=strategy_deps,
                engine=None,
                run_post_hooks_fn=AsyncMock(),
            )
    assert exc_no_engine.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_engine_retry_stage_mcp_retrieval_synthesis_matrix_and_max_retries(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify MCP tool retrieval enrichment, synthesis/matrix branches, CausalGraph output, and max retry limit."""
    gateway = SystemConfigMCPGateways(
        id="sys_0195f3a0000070008123456789abcdef",
        slug="search_gateway",
        endpoint_url="https://mcp.example.com/sse",
        tools=[],
    )
    in_memory_repo.set_mcp_gateways([gateway])

    matrix_blk = _create_matrix_block()
    stage1, stage2 = _build_stage1_and_stage2(
        repo=in_memory_repo,
        criteria_blocks=[matrix_blk],
        allowed_mcp_tools=["web_search"],
        user_payload="",
        global_source_text="",
    )
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
        expected_sdui_type="hero_insight",
    )
    ctx = _create_ctx()

    audit_trace = MCPAuditTrace(
        tool_id="web_search",
        step_name="sr_0195f3a0000070008123456789abcdef",
        query="quorum",
        duration_ms=42,
    )
    mcp_res = MCPRetrievalResultDTO(
        evidence_payload="<mcp_evidence>Verified fact</mcp_evidence>",
        audit_traces=[audit_trace],
        usage=TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10, cost_usd=0.001),
    )

    # 1. Matrix branch with MCP retrieval and max retries exceeded
    mock_matrix_engine = MagicMock()
    mock_matrix_engine.execute = AsyncMock(
        return_value=EngineExecutionResult.model_construct(
            results=[],
            hydrated_references={},
            synthesis_output=None,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.002),
        )
    )

    async def _always_retry_post_hook(
        *,
        step_obj: Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        raw_inputs_payload: Any = {"llm_anomaly_retry_requested": True, "results": []}
        updated = HookState.model_construct(
            execution_id=hook_state.execution_id,
            workflow_id=hook_state.workflow_id,
            step_id=hook_state.step_id,
            task_blueprint=hook_state.task_blueprint,
            metadata=hook_state.metadata,
            global_context_vars=GlobalContextVarsDTO(evaluative_matrices={"m1": 5.0}),
            inputs=raw_inputs_payload,
        )
        return updated, []

    mock_settings = MagicMock()
    mock_settings.llm_max_retries = 1

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage.LLMClient.from_tier",
        new=AsyncMock(return_value=MagicMock(spec=LLMClient, model_name="gemini-2.5-pro")),
    ):
        res_matrix = await execute_engine_retry_stage(
            stage1=stage1,
            stage2=stage2,
            step=step,
            context=ctx,
            deps=strategy_deps,
            engine=mock_matrix_engine,
            run_post_hooks_fn=_always_retry_post_hook,
            mcp_retrieval_fn=AsyncMock(return_value=mcp_res),
            settings_getter=lambda: mock_settings,
        )

    assert mock_matrix_engine.execute.await_count == 2
    assert res_matrix.final_dict["anomaly_unresolved"] is True
    assert "llm_anomaly_retry_requested" not in res_matrix.final_dict
    assert res_matrix.final_dict["evaluative_matrices"] == {"m1": 5.0}
    assert len(res_matrix.mcp_audit_traces) == 1
    assert res_matrix.usage_agg.total_tokens == 30

    # 2. SynthesisEngine branch with CausalGraphPayloadDTO output and non-empty initial payload
    rule_blk = _create_rule_block()
    stage1_syn, stage2_syn = _build_stage1_and_stage2(
        repo=in_memory_repo,
        criteria_blocks=[rule_blk],
        allowed_mcp_tools=["web_search"],
        user_payload="Initial user payload",
        global_source_text="Initial source text",
    )
    causal_dto = CausalGraphPayloadDTO(
        nodes=[],
        edges=[],
        root_cause_node_ids=[],
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=[],
    )
    mock_syn_engine = MagicMock(spec=SynthesisEngine)
    mock_syn_engine.execute = AsyncMock(
        return_value=EngineExecutionResult(
            results=[],
            hydrated_references={},
            synthesis_output=causal_dto,
            usage=None,
        )
    )

    async def _passthrough_post_hook(
        *,
        step_obj: Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        return hook_state, []

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage.LLMClient.from_tier",
        new=AsyncMock(return_value=MagicMock(spec=LLMClient, model_name="gemini-2.5-flash")),
    ):
        res_syn = await execute_engine_retry_stage(
            stage1=stage1_syn,
            stage2=stage2_syn,
            step=step,
            context=ctx,
            deps=strategy_deps,
            engine=mock_syn_engine,
            run_post_hooks_fn=_passthrough_post_hook,
            mcp_retrieval_fn=AsyncMock(return_value=mcp_res),
            settings_getter=lambda: mock_settings,
        )

    assert res_syn.final_dict["graph"] == causal_dto
    assert res_syn.dynamic_schema is not None

    # 3. Mapping and primitive synthesis_output branches + None post_hook_state.inputs
    raw_cases: list[tuple[Any, Any]] = [
        ({"k1": "v1", "k2": None}, ExecutionInputsDTO(dynamic_inputs={"k1": "v1"})),
        ("plain text synthesis", None),
    ]
    for raw_syn_out, expected_hook_inputs in raw_cases:
        mock_other_engine = MagicMock()
        mock_other_engine.execute = AsyncMock(
            return_value=EngineExecutionResult.model_construct(
                results=[],
                hydrated_references={},
                synthesis_output=raw_syn_out,
                usage=None,
            )
        )

        async def _custom_post_hook(
            *,
            step_obj: Step,
            step: StepRule,
            hook_state: HookState,
            hook_deps: HookDependencies,
            _inputs: Any = expected_hook_inputs,
        ) -> tuple[HookState, list[TraceEvent]]:
            return HookState.model_construct(
                execution_id=hook_state.execution_id,
                workflow_id=hook_state.workflow_id,
                step_id=hook_state.step_id,
                task_blueprint=hook_state.task_blueprint,
                metadata=hook_state.metadata,
                global_context_vars=hook_state.global_context_vars,
                inputs=_inputs,
            ), []

        with patch(
            "backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage.LLMClient.from_tier",
            new=AsyncMock(return_value=MagicMock(spec=LLMClient, model_name="gpt-4o-mini")),
        ):
            res_other = await execute_engine_retry_stage(
                stage1=stage1_syn,
                stage2=stage2_syn,
                step=step,
                context=ctx,
                deps=strategy_deps,
                engine=mock_other_engine,
                run_post_hooks_fn=_custom_post_hook,
                mcp_retrieval_fn=AsyncMock(
                    return_value=MCPRetrievalResultDTO(
                        evidence_payload="",
                        audit_traces=[],
                        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    )
                ),
            )
        if expected_hook_inputs is None:
            assert res_other.final_dict == {}
        else:
            assert res_other.final_dict == {"k1": "v1"}

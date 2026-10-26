"""Unit tests for Stage 4 telemetry metric merging, StepTraceMetadataDTO hydration, and TraceEvent emission."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import ExecutionInputsDTO, GlobalContextVarsDTO, HookDependencies, HookState
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import ProtocolPromptBlock, SystemRulePromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionResult
from backend_v2.models.dtos.prompt import PromptMappingDTO
from backend_v2.models.dtos.trace import StepTraceMetadataDTO
from backend_v2.models.enums import (
    CognitiveTier,
    EngineType,
    PromptBlockCategory,
    StepType,
    StepZone,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptPayload
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult,
    NodeStatePayload,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage import (
    EngineRetryStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.trace_event_stage import (
    build_llm_step_trace_events,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.utils.alias_engine import AliasEngine


class _DummyDynamicSchema(BaseModel):
    """Strict dummy schema for testing generated_schema serialization in TraceEventMetadataDTO."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    answer: str


def _build_stages_for_trace(
    *,
    state_data: dict[str, NodeStatePayload],
    final_dict: dict[str, DomainInputValue],
    engine_result: EngineExecutionResult | None,
    retrieval_usage: TokenUsage,
    usage_agg: TokenUsage,
    dynamic_schema: type[BaseModel] | None = None,
    cognitive_tier: CognitiveTier | str | None = CognitiveTier.BALANCED,
) -> tuple[BlueprintStageResult, PromptAndSchemaStageResult, EngineRetryStageResult]:
    """Build Stage 1, Stage 2, and Stage 3 results for Stage 4 unit testing."""
    repo = InMemoryUnifiedWorkflowRepository()
    proto_blk = ProtocolPromptBlock(
        id="blk_a000000000000002",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol", "fi": "Protokolla"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract exact quotes.",
    )
    rule_blk = SystemRulePromptBlock(
        id="blk_0123456789abcdef",
        slug="rule-blk",
        label=I18nText(translations={"en": "Rule", "fi": "Saanto"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        instruction_text="Evaluate carefully.",
    )
    raw_tier: Any = cognitive_tier
    step_obj = Step.model_construct(
        id="stp_0123456789abcdef",
        slug="test-step",
        name=I18nText(translations={"en": "Test Step", "fi": "Testivaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=raw_tier,
        extraction_protocol_block_id=proto_blk.id,
        criteria_block_ids=[rule_blk.id],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        is_system_core=False,
    )
    profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="default-prf",
        workflow_id="wf_0123456789abcdef",
        name=I18nText(translations={"en": "Default"}),
        target_block_order=[],
    )
    inputs_dto = ExecutionInputsDTO(raw_inputs={"doc": "Source text."})
    hook_state = HookState(
        execution_id="exe_0123456789abcdef",
        workflow_id="wf_0123456789abcdef",
        step_id="sr_0123456789abcdef",
        task_blueprint=step_obj.id,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs_dto,
    )
    pre_event = TraceEvent(step_name="sr_0123456789abcdef", event_type="input", content={"pre": True})
    post_event = TraceEvent(step_name="sr_0123456789abcdef", event_type="decision", content={"post": True})

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
        pre_events=[pre_event],
        block_map={rule_blk.id: rule_blk, proto_blk.id: proto_blk},
        role_block=None,
        protocol_block=proto_blk,
        execution_persona_block=None,
        criteria_blocks_models=[rule_blk],
        output_profile_id=profile.id,
        output_profile=profile,
        target_locale="en",
        global_source_text="Source text.",
        state_data=state_data,
        inputs_payload=inputs_dto,
    )
    stage2 = PromptAndSchemaStageResult(
        hook_state=hook_state,
        criteria_blocks=[rule_blk],
        matrix_block=None,
        hydrated_shuffled_atoms=None,
        alias_engine=AliasEngine(),
        prompt_payload=PromptPayload(
            base_system_prompt="Static base.",
            user_payload="Dynamic user.",
            atom_to_block_ids={},
        ),
        user_payload="Dynamic user.",
        target_chunks=[["chunk_0"], ["chunk_1"]],
        dynamic_schema=dynamic_schema,
        is_synthesis_step=False,
        source_doc_ctx=[],
        input_mappings=PromptMappingDTO(mappings={}),
        schema_map={},
        blueprint_labels={},
    )
    mock_client = MagicMock()
    mock_client.model_name = "vertex_ai/gemini-2.5-pro"
    audit_trace = MCPAuditTrace(
        tool_id="web_search",
        step_name="sr_0123456789abcdef",
        query="test",
        duration_ms=15,
    )
    stage3 = EngineRetryStageResult(
        hook_state=hook_state,
        final_dict=final_dict,
        post_events=[post_event],
        engine_result=engine_result,
        mcp_audit_traces=[audit_trace],
        bound_client=mock_client,
        retrieval_usage=retrieval_usage,
        usage_agg=usage_agg,
        latency_ms=125,
        context_char_length=42,
        dynamic_schema=dynamic_schema,
        prompt_contexts=["ctx_1"],
    )
    return stage1, stage2, stage3


def test_llm_strategy_propagates_engine_usage_to_trace_event() -> None:
    """Verify build_llm_step_trace_events propagates engine_result.usage and profiler_metrics into TraceEvent."""
    engine_usage = TokenUsage(prompt_tokens=500, completion_tokens=100, total_tokens=600, cost_usd=0.025)
    zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0, cost_usd=0.0)
    engine_res = EngineExecutionResult(results=[], hydrated_references={}, usage=engine_usage)

    stage1, stage2, stage3 = _build_stages_for_trace(
        state_data={
            "profiler_metrics": {"cpu_ms": 12},
            "_audit_signature": "sig_abc123",
        },
        final_dict={"results": []},
        engine_result=engine_res,
        retrieval_usage=zero_usage,
        usage_agg=zero_usage,
        dynamic_schema=_DummyDynamicSchema,
        cognitive_tier=CognitiveTier.BALANCED,
    )
    step = StepRule(id="sr_0123456789abcdef", task_blueprint="stp_0123456789abcdef", input_mappings={})
    mock_engine = MagicMock()
    mock_engine.telemetry_strategy_label = "tda_engine"

    traces = build_llm_step_trace_events(
        stage1=stage1,
        stage2=stage2,
        stage3=stage3,
        step=step,
        engine=mock_engine,
    )

    assert len(traces) == 3
    assert traces[0].event_type == "input"
    assert traces[1].event_type == "decision"
    output_trace = traces[2]
    assert output_trace.event_type == "output"
    content_map: Any = output_trace.content
    assert content_map["profiler_metrics"] == {"cpu_ms": 12}
    assert content_map["_audit_signature"] == "sig_abc123"
    step_meta = StepTraceMetadataDTO.model_validate(content_map["_step_metadata"])
    assert step_meta.model_strategy == "tda_engine"
    assert step_meta.cognitive_tier == CognitiveTier.BALANCED.value
    assert step_meta.physical_model == "vertex_ai/gemini-2.5-pro"
    assert step_meta.token_usage is not None
    assert step_meta.token_usage.total_tokens == 600
    assert step_meta.token_usage.cost_usd == 0.025
    assert output_trace.metadata is not None
    assert output_trace.metadata.chunk_size == 2
    assert output_trace.metadata.latency_ms == 125
    assert output_trace.metadata.generated_schema is not None
    generated_schema_map: Any = output_trace.metadata.generated_schema
    assert "answer" in generated_schema_map["properties"]


def test_trace_event_stage_combines_existing_step_metadata_usage_with_retrieval_usage_and_fallbacks() -> None:
    """Verify existing _step_metadata token_usage is summed with retrieval_usage and non-str label falls back."""
    existing_usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, cost_usd=0.01)
    retrieval_usage = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30, cost_usd=0.002)

    stage1, stage2, stage3 = _build_stages_for_trace(
        state_data={
            "_step_metadata": {
                "execution_id": "exe_0123456789abcdef",
                "workflow_id": "wf_0123456789abcdef",
                "step_id": "sr_0123456789abcdef",
                "token_usage": existing_usage.model_dump(),
            }
        },
        final_dict={"output": "ok"},
        engine_result=None,
        retrieval_usage=retrieval_usage,
        usage_agg=retrieval_usage,
        dynamic_schema=None,
        cognitive_tier="fast",
    )
    step = StepRule(id="sr_0123456789abcdef", task_blueprint="stp_0123456789abcdef", input_mappings={})
    mock_engine = MagicMock()
    mock_engine.telemetry_strategy_label = 12345  # Non-string label triggers "prompt" fallback

    traces = build_llm_step_trace_events(
        stage1=stage1,
        stage2=stage2,
        stage3=stage3,
        step=step,
        engine=mock_engine,
    )

    output_trace = traces[-1]
    fallback_content_map: Any = output_trace.content
    step_meta = StepTraceMetadataDTO.model_validate(fallback_content_map["_step_metadata"])
    assert step_meta.model_strategy == "prompt"
    assert step_meta.cognitive_tier == "fast"
    assert step_meta.token_usage is not None
    assert step_meta.token_usage.total_tokens == 180
    assert abs(step_meta.token_usage.cost_usd - 0.012) < 1e-6
    assert output_trace.metadata is not None
    assert output_trace.metadata.generated_schema is None

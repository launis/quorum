"""Unit tests for Stage 2 context building, prompt compilation, atom chunking, and schema resolution."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest

from backend_v2.core.hook_registry import ExecutionInputsDTO, GlobalContextVarsDTO, HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.matrix import FlattenedAtom, MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EngineType,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
    StepZone,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_EXTENSION,
    _SCHEMA_BLOCK_MATRIX,
    _SCHEMA_BLOCK_SYSTEM,
    _SCHEMA_BLOCK_TEXT,
    BlueprintStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult,
    execute_prompt_and_schema_stage,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_rule_block(block_id: str, output_extensions: list[str] | None = None) -> SystemRulePromptBlock:
    """Create a valid SystemRulePromptBlock for Stage 2 testing."""
    return SystemRulePromptBlock(
        id=block_id,
        slug=f"slug-{block_id[-4:]}",
        label=I18nText(translations={"en": f"Block {block_id}", "fi": f"Lohko {block_id}"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        instruction_text="Evaluate the target document carefully.",
        output_extensions=output_extensions if output_extensions is not None else [],
    )


def _create_matrix_block(block_id: str, output_extensions: list[str] | None = None) -> MatrixPromptBlock:
    """Create a valid MatrixPromptBlock with two scales and TDA assertions for Stage 2 testing."""
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
        slug=f"matrix-{block_id[-4:]}",
        label=I18nText(translations={"en": "Matrix", "fi": "Matriisi"}),
        description=I18nText(translations={"en": "Matrix Desc", "fi": "Matriisin kuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        ai_description="Evaluate against theoretical matrix.",
        scales=[
            MatrixScale(score=1, ai_label="Novice", claims=[claim]),
            MatrixScale(score=5, ai_label="Expert", claims=[claim]),
        ],
        output_extensions=output_extensions if output_extensions is not None else [],
    )


def _create_default_profile(workflow_id: str = "wf_0195f3a0000070008123456789abcdef") -> OutputProfile:
    """Create a valid default OutputProfile for Stage 2 testing."""
    return OutputProfile(
        id="prf_0195f3a0000070008123456789abcdef",
        slug="default-prf",
        workflow_id=workflow_id,
        name=I18nText(translations={"en": "Default"}),
        target_block_order=[],
    )


def _create_ctx(
    *,
    execution_id: str = "exe_0195f3a0000070008123456789abcdef",
    workflow_id: str = "wf_0195f3a0000070008123456789abcdef",
    output_profile_id: str = "prf_0195f3a0000070008123456789abcdef",
    expected_inputs: list[ExpectedInput] | None = None,
) -> StrategyContext:
    """Create a valid StrategyContext for Stage 2 testing."""
    return StrategyContext(
        execution_id=execution_id,
        workflow_id=workflow_id,
        output_profile_id=output_profile_id,
        target_locale="en",
        cognitive_tier=CognitiveTier.FAST,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        context_variables=ContextVariablesDTO(),
        prompt_blocks=[],
        expected_inputs=expected_inputs if expected_inputs is not None else [],
    )


def _build_stage1_result(
    *,
    repo: InMemoryUnifiedWorkflowRepository,
    criteria_blocks: list[PromptBlock],
    output_profile: OutputProfile,
    hook_state: HookState,
    workflow_obj: Workflow | None = None,
    block_map: dict[str, PromptBlock] | None = None,
) -> BlueprintStageResult:
    """Build a deterministic BlueprintStageResult for Stage 2 unit testing."""
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
        allowed_mcp_tools=[],
        mcp_tool_params={},
        is_system_core=False,
    )
    resolved_map = {b.id: b for b in criteria_blocks}
    resolved_map[proto_blk.id] = proto_blk
    if block_map is not None:
        resolved_map.update(block_map)

    inputs_dto = ExecutionInputsDTO(raw_inputs={"doc": "Primary source document text."})
    if isinstance(hook_state.inputs, ExecutionInputsDTO):
        inputs_dto = hook_state.inputs

    return BlueprintStageResult(
        step_obj=step_obj,
        workflow_obj=workflow_obj,
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
        block_map=resolved_map,
        role_block=None,
        protocol_block=proto_blk,
        execution_persona_block=None,
        criteria_blocks_models=criteria_blocks,
        output_profile_id=output_profile.id,
        output_profile=output_profile,
        target_locale="en",
        global_source_text="Primary source document text.",
        state_data={"inputs": {"doc": "Primary source document text."}},
        inputs_payload=inputs_dto,
    )


@pytest.fixture
def in_memory_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a stateful in-memory repository pre-populated with an ExecutionRecord."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.set_execution(
        ExecutionRecord(
            id="exe_0195f3a0000070008123456789abcdef",
            workflow_id="wf_0195f3a0000070008123456789abcdef",
            output_profile_id="prf_0195f3a0000070008123456789abcdef",
            target_locale="en",
            status=ExecutionStatus.RUNNING,
            metadata=ExecutionMetadata(),
            source_identity_manifest={"doc": "Uploaded Primary Document"},
        )
    )
    return repo


@pytest.fixture
def strategy_deps(in_memory_repo: InMemoryUnifiedWorkflowRepository) -> StrategyDependencies:
    """Provide StrategyDependencies wired to the in-memory repository and PromptCompiler."""
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
async def test_output_profile_directives_relocated_to_user_payload_and_system_prompt_invariant_neg09(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_prompt_and_schema_stage appends execution_parameters to user_payload with static system_prompt."""
    rule_block = _create_rule_block("blk_0195f3a0000070008123456789abcdef")
    profile_1 = OutputProfile(
        id="prf_0195f3a0000070008123456789abcde1",
        slug="formal-coaching",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        name=I18nText(translations={"en": "Formal Coaching"}),
        tone_instruction="Formal coaching tone, rigorous and objective.",
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070018111222233334444",
                title=I18nText(translations={"en": "Group 1"}),
                target_blocks=["*"],
            )
        ],
    )
    profile_2 = OutputProfile(
        id="prf_0195f3a0000070008123456789abcde2",
        slug="executive-summary",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        name=I18nText(translations={"en": "Executive Summary"}),
        tone_instruction="Concise executive summary for CEO.",
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070028222333344445555",
                title=I18nText(translations={"en": "Group 2"}),
                target_blocks=["*"],
            )
        ],
    )

    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "Primary source document text."}),
    )
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )

    stage1_a = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[rule_block],
        output_profile=profile_1,
        hook_state=hook_state,
    )
    stage1_b = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[rule_block],
        output_profile=profile_2,
        hook_state=hook_state,
    )

    ctx_1 = _create_ctx(output_profile_id=profile_1.id)
    ctx_2 = _create_ctx(output_profile_id=profile_2.id)

    res_1 = await execute_prompt_and_schema_stage(stage1=stage1_a, step=step, context=ctx_1, deps=strategy_deps)
    res_2 = await execute_prompt_and_schema_stage(stage1=stage1_b, step=step, context=ctx_2, deps=strategy_deps)

    hash_1 = hashlib.sha256(res_1.prompt_payload.base_system_prompt.encode()).hexdigest()
    hash_2 = hashlib.sha256(res_2.prompt_payload.base_system_prompt.encode()).hexdigest()
    assert hash_1 == hash_2
    assert "<execution_parameters>" not in res_1.prompt_payload.base_system_prompt
    assert "<tone_instruction>" not in res_1.prompt_payload.base_system_prompt
    assert "<execution_parameters>" in res_1.user_payload
    assert "<tone_instruction>Formal coaching tone, rigorous and objective.</tone_instruction>" in res_1.user_payload
    assert "grp_0195f3a0000070018111222233334444" in res_1.user_payload
    assert "grp_0195f3a0000070028222333344445555" not in res_1.user_payload
    assert "<tone_instruction>Concise executive summary for CEO.</tone_instruction>" in res_2.user_payload
    assert "grp_0195f3a0000070028222333344445555" in res_2.user_payload


@pytest.mark.asyncio
async def test_matrix_step_succeeds_when_shuffled_atoms_only_in_dynamic_inputs(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_prompt_and_schema_stage resolves shuffled_atoms and chunks matrix atoms via ChunkingService."""
    matrix_blk = _create_matrix_block("blk_0195f3a0000070058555555555555555")
    sample_atoms = [
        FlattenedAtom(
            atom_id="atm_0195f3a0000070018111111111111111",
            question="Question 1",
            depends_on=(),
            acceptance_criteria=(),
            anti_patterns=(),
            syntactic_anchors=(),
        ),
        FlattenedAtom(
            atom_id="atm_0195f3a0000070028222222222222222",
            question="Question 2",
            depends_on=(),
            acceptance_criteria=(),
            anti_patterns=(),
            syntactic_anchors=(),
        ),
    ]
    profile = _create_default_profile()
    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(shuffled_atoms=sample_atoms),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "Primary source document text."}),
    )
    stage1 = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[matrix_blk],
        output_profile=profile,
        hook_state=hook_state,
    )
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )
    ctx = _create_ctx(output_profile_id=profile.id)

    res = await execute_prompt_and_schema_stage(stage1=stage1, step=step, context=ctx, deps=strategy_deps)

    assert isinstance(res, PromptAndSchemaStageResult)
    assert res.matrix_block is not None and res.matrix_block.id == matrix_blk.id
    assert res.hydrated_shuffled_atoms is not None
    assert len(res.hydrated_shuffled_atoms) == 2
    assert len(res.target_chunks) >= 1
    assert len(res.source_doc_ctx) == 1
    assert res.source_doc_ctx[0].display_name == "Uploaded Primary Document"


@pytest.mark.asyncio
async def test_llm_strategy_missing_atoms_crash(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_prompt_and_schema_stage raises AppException when a matrix step lacks shuffled_atoms."""
    matrix_blk = _create_matrix_block("blk_0195f3a0000070058555555555555555")
    profile = _create_default_profile()
    hook_state_missing = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(shuffled_atoms=None),
        inputs=ExecutionInputsDTO(),
    )
    stage1 = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[matrix_blk],
        output_profile=profile,
        hook_state=hook_state_missing,
    )
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )
    ctx = _create_ctx(output_profile_id=profile.id)

    with pytest.raises(AppException, match="Matrix step missing 'shuffled_atoms' in global_context_vars") as exc_info:
        await execute_prompt_and_schema_stage(stage1=stage1, step=step, context=ctx, deps=strategy_deps)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # Empty list boundary check
    hook_state_empty = hook_state_missing.model_copy(
        update={"global_context_vars": GlobalContextVarsDTO(shuffled_atoms=[])}
    )
    stage1_empty = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[matrix_blk],
        output_profile=profile,
        hook_state=hook_state_empty,
    )
    with pytest.raises(AppException, match="Strict Fail-Fast Enforced: 'shuffled_atoms' is empty"):
        await execute_prompt_and_schema_stage(stage1=stage1_empty, step=step, context=ctx, deps=strategy_deps)


@pytest.mark.asyncio
async def test_causal_discovery_step_with_cohesion_matrix_skips_shuffled_atoms(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify CAUSAL_DISCOVERY step with MatrixPromptBlock cohesion rubric succeeds without shuffled_atoms."""
    cohesion_matrix_blk = _create_matrix_block("blk_0195f3a00000700c80a1e50000000001")
    profile = _create_default_profile(workflow_id="wf_0195f3a00000700a88f1d71000000001")
    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a00000700a88f1d71000000001",
        step_id="sr_0195f3a00000700a88f1d71000000002",
        task_blueprint="stp_0195f3a00000700c84a5a1d15c00438a",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(shuffled_atoms=None),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "Primary source document text."}),
    )
    base_stage1 = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[cohesion_matrix_blk],
        output_profile=profile,
        hook_state=hook_state,
    )
    causal_step_obj = base_stage1.step_obj.model_copy(
        update={
            "id": "stp_0195f3a00000700c84a5a1d15c00438a",
            "slug": "step_causal_discovery",
            "type": StepType.CAUSAL_DISCOVERY,
            "engine_type": EngineType.CAUSAL_DISCOVERY,
            "criteria_block_ids": [cohesion_matrix_blk.id],
        }
    )
    stage1_causal = BlueprintStageResult(
        step_obj=causal_step_obj,
        workflow_obj=base_stage1.workflow_obj,
        hook_state=base_stage1.hook_state,
        hook_deps=base_stage1.hook_deps,
        pre_events=base_stage1.pre_events,
        block_map=base_stage1.block_map,
        role_block=base_stage1.role_block,
        protocol_block=base_stage1.protocol_block,
        execution_persona_block=base_stage1.execution_persona_block,
        criteria_blocks_models=base_stage1.criteria_blocks_models,
        output_profile_id=base_stage1.output_profile_id,
        output_profile=base_stage1.output_profile,
        target_locale=base_stage1.target_locale,
        global_source_text=base_stage1.global_source_text,
        state_data=base_stage1.state_data,
        inputs_payload=base_stage1.inputs_payload,
    )
    step = StepRule(
        id="sr_0195f3a00000700a88f1d71000000002",
        task_blueprint="stp_0195f3a00000700c84a5a1d15c00438a",
        input_mappings={},
    )
    ctx = _create_ctx(
        workflow_id="wf_0195f3a00000700a88f1d71000000001",
        output_profile_id=profile.id,
    )

    res = await execute_prompt_and_schema_stage(stage1=stage1_causal, step=step, context=ctx, deps=strategy_deps)

    assert isinstance(res, PromptAndSchemaStageResult)
    assert res.hydrated_shuffled_atoms is None
    assert res.target_chunks == [None]
    assert res.matrix_block is not None and res.matrix_block.id == cohesion_matrix_blk.id


@pytest.mark.asyncio
async def test_prompt_and_schema_stage_resolves_schema_map_and_dynamic_schema_with_frozen_ctx(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify workflow schema_map resolution, mapping global_context_vars, and frozen_ctx schema compilation."""
    role_blk = PersonaPromptBlock(
        id="blk_0195f3a0000070018111111111111111",
        slug="role-blk",
        label=I18nText(translations={"en": "Role"}),
        description=I18nText(translations={"en": "Role"}),
        category_id=PromptBlockCategory.AGENT_ROLE,
        role_enforcement="Act as auditor.",
    )
    proto_blk = ProtocolPromptBlock(
        id="blk_0195f3a0000070028222222222222222",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol"}),
        description=I18nText(translations={"en": "Protocol"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract quotes.",
    )
    pers_blk = PersonaPromptBlock(
        id="blk_0195f3a0000070038333333333333333",
        slug="pers-blk",
        label=I18nText(translations={"en": "Persona"}),
        description=I18nText(translations={"en": "Persona"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        role_enforcement="Strict persona.",
    )
    matrix_blk = _create_matrix_block("blk_0195f3a0000070048444444444444444", output_extensions=["ext_matrix_1"])
    text_blk = _create_rule_block("blk_0195f3a0000070058555555555555555", output_extensions=["ext_text_1"])

    bp_matrix = Step(
        id="stp_0195f3a0000070018111111111111111",
        slug="bp-matrix",
        name=I18nText(translations={"en": "Matrix Blueprint"}),
        description=I18nText(translations={"en": "Matrix Blueprint"}),
        type=StepType.LLM,
        engine_type=EngineType.TDA,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        role_block_id=role_blk.id,
        extraction_protocol_block_id=proto_blk.id,
        execution_persona_block_id=pers_blk.id,
        criteria_block_ids=[matrix_blk.id],
        mcp_tool_params={},
    )
    bp_text = Step(
        id="stp_0195f3a0000070028222222222222222",
        slug="bp-text",
        name=I18nText(translations={"en": "Text Blueprint"}),
        description=I18nText(translations={"en": "Text Blueprint"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        extraction_protocol_block_id=proto_blk.id,
        criteria_block_ids=[text_blk.id],
        mcp_tool_params={},
    )
    in_memory_repo.seed_raw_step(bp_matrix.id, bp_matrix)
    in_memory_repo.seed_raw_step(bp_text.id, bp_text)

    wf = Workflow(
        id="wf_0195f3a0000070008123456789abcdef",
        slug="wf-schema",
        name=I18nText(translations={"en": "Workflow"}),
        description=I18nText(translations={"en": "Workflow"}),
        status="published",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        steps=[
            StepRule(id="sr_0195f3a0000070018111111111111111", task_blueprint=bp_matrix.id),
            StepRule(id="sr_0195f3a0000070028222222222222222", task_blueprint=bp_text.id),
        ],
    )
    profile = _create_default_profile(workflow_id=wf.id)
    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id=wf.id,
        step_id="sr_0195f3a0000070028222222222222222",
        task_blueprint=bp_text.id,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        inputs=ExecutionInputsDTO(raw_inputs={"inputs": {"doc": "Nested source text."}}),
    )
    stage1 = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[text_blk],
        output_profile=profile,
        hook_state=hook_state,
        workflow_obj=wf,
        block_map={
            role_blk.id: role_blk,
            proto_blk.id: proto_blk,
            pers_blk.id: pers_blk,
            matrix_blk.id: matrix_blk,
            text_blk.id: text_blk,
        },
    )
    step = StepRule(
        id="sr_0195f3a0000070028222222222222222",
        task_blueprint=bp_text.id,
        input_mappings={"doc": "$inputs.doc"},
    )
    ctx = _create_ctx(
        workflow_id=wf.id,
        output_profile_id=profile.id,
        expected_inputs=[
            ExpectedInput(
                input_key="doc",
                label=I18nText(translations={"en": "Doc"}),
                required=True,
                input_modes=["text"],
                description=I18nText(translations={"en": "Doc"}),
            )
        ],
    )
    synth_engine = MagicMock(spec=SynthesisEngine)

    res = await execute_prompt_and_schema_stage(
        stage1=stage1,
        step=step,
        context=ctx,
        deps=strategy_deps,
        frozen_ctx=FrozenContext(),
        engine=synth_engine,
    )

    assert res.is_synthesis_step is True
    assert res.dynamic_schema is not None
    assert res.schema_map["sr_0195f3a0000070018111111111111111"] == _SCHEMA_BLOCK_MATRIX
    assert res.schema_map["sr_0195f3a0000070028222222222222222"] == _SCHEMA_BLOCK_TEXT
    assert res.schema_map["ext_matrix_1"] == _SCHEMA_BLOCK_EXTENSION
    assert res.schema_map["_step_metadata"] == _SCHEMA_BLOCK_SYSTEM
    assert res.blueprint_labels["sr_0195f3a0000070018111111111111111"] == "Matrix Blueprint"
    assert res.blueprint_labels["sr_0195f3a0000070028222222222222222"] == "Text Blueprint"
    assert len(res.source_doc_ctx) == 1
    assert res.source_doc_ctx[0].text_content == "Nested source text."


@pytest.mark.asyncio
async def test_prompt_and_schema_stage_execution_record_and_serialization_errors(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify negative error paths for ExecutionRecord lookup, hydration, and group serialization."""
    test_logger = logging.getLogger("backend_v2.services.orchestrator.strategies.llm_strategy")
    rule_block = _create_rule_block("blk_0195f3a0000070008123456789abcdef")
    profile = OutputProfile(
        id="prf_0195f3a0000070008123456789abcdef",
        slug="default-prf",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        name=I18nText(translations={"en": "Default"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008123456789abcdef",
                title=I18nText(translations={"en": "Group"}),
                target_blocks=["*"],
            )
        ],
    )
    hook_state = HookState(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "Primary source document text."}),
    )
    stage1 = _build_stage1_result(
        repo=in_memory_repo,
        criteria_blocks=[rule_block],
        output_profile=profile,
        hook_state=hook_state,
    )
    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        input_mappings={},
    )
    ctx = _create_ctx(output_profile_id=profile.id)

    # 1. Serialization failure in json.dumps -> VALIDATION_FAILED
    calls = 0
    real_dumps: Callable[..., str] = json.dumps

    def _fail_first_dumps(*args: object, **kwargs: object) -> str:
        """Simulate serialization failure on first invocation while allowing logging serialization."""
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TypeError("unserializable")
        return real_dumps(*args, **kwargs)

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage.json.dumps",
        side_effect=_fail_first_dumps,
    ):
        with pytest.raises(AppException, match="VALIDATION_FAILED") as exc_info:
            await execute_prompt_and_schema_stage(
                stage1=stage1,
                step=step,
                context=ctx,
                deps=strategy_deps,
                step_logger=test_logger,
            )
        assert "Failed to serialize matrix_synthesis_groups" in str(exc_info.value.details)

    # 2. Corrupted ExecutionRecord in DB -> VALIDATION_FAILED
    in_memory_repo.set_execution({"id": "exe_corrupt01234567", "bad_field": 123})
    ctx_corrupt = ctx.model_copy(update={"execution_id": "exe_corrupt01234567"})
    with caplog.at_level(logging.ERROR, logger="backend_v2.services.orchestrator.strategies.llm_strategy"):
        with pytest.raises(
            AppException, match="Failed to parse execution record for source documents context"
        ) as exc_info:
            await execute_prompt_and_schema_stage(
                stage1=stage1,
                step=step,
                context=ctx_corrupt,
                deps=strategy_deps,
                step_logger=test_logger,
            )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 3. Repository get_execution fault -> RESOURCE_NOT_FOUND
    in_memory_repo.inject_fault("get_execution", RuntimeError("DB offline"))
    try:
        with pytest.raises(
            AppException, match="Execution record 'exe_0195f3a0000070008123456789abcdef' not found"
        ) as exc_info:
            await execute_prompt_and_schema_stage(
                stage1=stage1,
                step=step,
                context=ctx,
                deps=strategy_deps,
                step_logger=test_logger,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    finally:
        in_memory_repo.clear_faults()

"""Unit tests for Stage 1 blueprint resolution, pre-hooks, and step context metadata extraction."""

from __future__ import annotations

import functools
import logging
from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import ExecutionInputsDTO, GlobalContextVarsDTO, HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.blackboard import DraftAtomList, GlobalAtomBlackboard
from backend_v2.models.domain.output_profile import MatrixSynthesisGroup, OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import (
    CognitiveTier,
    EngineType,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
    StepZone,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult,
    dlq_handle_debug_log_error,
    execute_blueprint_and_pre_hooks_stage,
    extract_step_context_metadata,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_rule_block(block_id: str) -> SystemRulePromptBlock:
    """Create a valid SystemRulePromptBlock for Stage 1 testing."""
    return SystemRulePromptBlock(
        id=block_id,
        slug=f"slug-{block_id[-4:]}",
        label=I18nText(translations={"en": f"Block {block_id}", "fi": f"Lohko {block_id}"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        instruction_text="Evaluate the target document carefully.",
        output_extensions=[],
    )


def _create_context(
    *,
    output_profile_id: str | None = "prf_0195f3a0000070008123456789abcdef",
    target_locale: str = "fi",
    context_variables: ContextVariablesDTO | None = None,
) -> StrategyContext:
    """Create a valid StrategyContext for Stage 1 testing."""
    resolved_vars = ContextVariablesDTO()
    if context_variables is not None:
        resolved_vars = context_variables
    return StrategyContext(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        strictness_level=50,
        output_profile_id=output_profile_id,
        target_locale=target_locale,
        cognitive_tier=CognitiveTier.BALANCED,
        metadata=ExecutionMetadata(),
        context_variables=resolved_vars,
    )


@pytest.fixture
def in_memory_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a stateful in-memory repository pre-populated with baseline Stage 1 entities."""
    repo = InMemoryUnifiedWorkflowRepository()
    proto_blk = ProtocolPromptBlock(
        id="blk_0195f3a00000700a8000000000000002",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol", "fi": "Protokolla"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract exact quotes.",
    )
    repo.seed_raw_prompt_block(proto_blk.id, proto_blk)
    repo.seed_raw_prompt_block(
        "blk_0195f3a0000070008123456789abcdef", _create_rule_block("blk_0195f3a0000070008123456789abcdef")
    )
    step = Step(
        id="stp_0195f3a0000070008123456789abcdef",
        slug="test-step",
        name=I18nText(translations={"en": "Test Step", "fi": "Testivaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        extraction_protocol_block_id=proto_blk.id,
        criteria_block_ids=["blk_0195f3a0000070008123456789abcdef"],
        is_system_core=False,
    )
    repo.seed_raw_step(step.id, step)
    repo.set_output_profiles(
        [
            OutputProfile(
                id="prf_0195f3a0000070008123456789abcdef",
                slug="default-prf",
                workflow_id="wf_0195f3a0000070008123456789abcdef",
                name=I18nText(translations={"en": "Default Profile", "fi": "Oletusprofiili"}),
                description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
                tone_instruction="Maintain a formal tone.",
                matrix_synthesis_groups=[
                    MatrixSynthesisGroup(
                        id="grp_0195f3a0000070008123456789abcdef",
                        title=I18nText(translations={"en": "Group", "fi": "Ryhma"}),
                        target_blocks=["*"],
                    )
                ],
            )
        ]
    )
    repo.set_workflow(
        Workflow(
            id="wf_0195f3a0000070008123456789abcdef",
            slug="test-wf",
            name=I18nText(translations={"en": "Test Workflow", "fi": "Testityonkulku"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            status="published",
            version=1,
            historical_context_mode=HistoricalContextMode.DISABLED,
            model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
            steps=[
                StepRule(
                    id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
                )
            ],
            expected_inputs=[
                ExpectedInput(
                    input_key="doc",
                    label=I18nText(translations={"en": "Doc", "fi": "Dokumentti"}),
                    required=True,
                    input_modes=["text"],
                    description=I18nText(translations={"en": "Doc", "fi": "Dokumentti"}),
                )
            ],
        )
    )
    return repo


@pytest.fixture
def strategy_deps(in_memory_repo: InMemoryUnifiedWorkflowRepository) -> StrategyDependencies:
    """Provide StrategyDependencies wired to the in-memory repository."""
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


async def _noop_pre_hooks(
    step_obj: Step,
    step_rule: StepRule,
    hook_state: HookState,
    hook_deps: HookDependencies,
) -> tuple[HookState, list[TraceEvent]]:
    """Return hook_state unchanged with no pre-hook events."""
    return hook_state, []


def test_dlq_handle_debug_log_error_emits_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Verify dlq_handle_debug_log_error logs a structured warning message."""
    test_logger = logging.getLogger("backend_v2.services.orchestrator.strategies.llm_strategy")
    with caplog.at_level(logging.WARNING, logger="backend_v2.services.orchestrator.strategies.llm_strategy"):
        dlq_handle_debug_log_error(RuntimeError("disk full"), step_logger=test_logger)

    assert any("Failed to write debug prompt log: disk full" in r.message for r in caplog.records)


def test_extract_step_context_metadata_dto_and_atom_branches() -> None:
    """Verify extract_step_context_metadata extracts gvars, doc_aliases, and AtomResultDTO dag_results."""
    atom_1 = AtomResultDTO(
        tda_id="tda_0195f3a0000070008123456789abcdef",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Direct atom DTO",
        contextual_override=True,
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_0195f3a00000700f8edcba9876543210",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Standalone atom DTO",
        contextual_override=False,
    )
    atom_3 = AtomResultDTO(
        tda_id="tda_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Nested results atom DTO",
        contextual_override=True,
    )

    hook_state = HookState.model_construct(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        inputs=ExecutionInputsDTO.model_construct(
            raw_inputs={
                "list_atoms": [
                    atom_1,
                    {"atom_id": "tda_0195f3a00000700a8aaa1111bbbb2222"},
                    {"tda_id": "tda_0195f3a00000700c8ccc3333dddd4444", "evaluation_reasoning": "Custom"},
                ],
                "single_atom": atom_2,
            },
            dynamic_inputs={
                "nested_step": {
                    "results": [
                        atom_3,
                        {"atom_id": "tda_0195f3a00000700e8eee5555ffff6666"},
                        {"tda_id": "tda_0195f3a0000070098999888877776666"},
                    ]
                }
            },
        ),
    )

    blackboard = GlobalAtomBlackboard(
        atoms_by_input={"doc_a": DraftAtomList(atoms=[])},
    )
    ctx = _create_context(context_variables=ContextVariablesDTO(global_atom_blackboard=blackboard))

    meta = extract_step_context_metadata(hook_state, ctx)
    assert meta.gvars["language"] == "fi"
    assert meta.doc_aliases == ["doc_a"]
    assert "tda_0195f3a0000070008123456789abcdef" in meta.dag_results
    assert "tda_0195f3a00000700f8edcba9876543210" in meta.dag_results
    assert "tda_0195f3a0000070018111222233334444" in meta.dag_results
    assert meta.dag_results["tda_0195f3a00000700a8aaa1111bbbb2222"].status == ExecutionStatus.PASSED
    assert meta.dag_results["tda_0195f3a00000700a8aaa1111bbbb2222"].contextual_override is True
    assert meta.dag_results["tda_0195f3a00000700c8ccc3333dddd4444"].evaluation_reasoning == "Custom"
    assert meta.dag_results["tda_0195f3a00000700e8eee5555ffff6666"].evaluation_reasoning == "Extracted"
    assert meta.dag_results["tda_0195f3a0000070098999888877776666"].status == ExecutionStatus.PASSED


def test_extract_step_context_metadata_mapping_gvars_and_default_aliases() -> None:
    """Verify extract_step_context_metadata handles mapping gvars and defaults doc_aliases to N/A."""
    hook_state = HookState.model_construct(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wf_0195f3a0000070008123456789abcdef",
        step_id="step_1",
        task_blueprint="stp_0195f3a0000070008123456789abcdef",
        global_context_vars={"strictness_level": 40},
        inputs=ExecutionInputsDTO(raw_inputs={"plain": "text"}, dynamic_inputs={}),
    )
    meta = extract_step_context_metadata(hook_state, None)
    assert meta.gvars == {"strictness_level": 40}
    assert meta.doc_aliases == ["N/A"]
    assert meta.dag_results == {}


@pytest.mark.asyncio
async def test_execute_with_role_and_persona_and_protocol(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify execute_blueprint_and_pre_hooks_stage resolves role, protocol, persona, criteria, and OutputProfile."""
    role_blk = PersonaPromptBlock(
        id="blk_0195f3a00000700a8000000000000001",
        slug="role-blk",
        label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.AGENT_ROLE,
        role_enforcement="Act as auditor.",
    )
    proto_blk = ProtocolPromptBlock(
        id="blk_0195f3a00000700a8000000000000002",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol", "fi": "Protokolla"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract exact quotes.",
    )
    persona_blk = PersonaPromptBlock(
        id="blk_0195f3a00000700a8000000000000003",
        slug="pers-blk",
        label=I18nText(translations={"en": "Persona", "fi": "Persoona"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        role_enforcement="Strict evaluator.",
    )
    crit_blk = _create_rule_block("blk_0195f3a00000700a8000000000000004")

    for b in (role_blk, proto_blk, persona_blk, crit_blk):
        in_memory_repo.seed_raw_prompt_block(b.id, b)

    step_def = Step(
        id="stp_0195f3a00000700a8000000000000001",
        slug="full-step",
        name=I18nText(translations={"en": "Full Step", "fi": "Taysi vaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        role_block_id=role_blk.id,
        extraction_protocol_block_id=proto_blk.id,
        execution_persona_block_id=persona_blk.id,
        criteria_block_ids=[crit_blk.id],
        is_system_core=False,
    )
    in_memory_repo.seed_raw_step(step_def.id, step_def)

    step_rule = StepRule(
        id="sr_0195f3a00000700a8000000000000001",
        task_blueprint=step_def.id,
        input_mappings={"doc": "$inputs.doc"},
    )
    projector = StateProjector(
        [
            TraceEvent(
                step_name="inputs",
                event_type="input",
                content=ExecutionInputsDTO(raw_inputs={"doc": "Primary source content."}),
            )
        ]
    )
    ctx = _create_context()

    result = await execute_blueprint_and_pre_hooks_stage(
        step=step_rule,
        projector=projector,
        context=ctx,
        deps=strategy_deps,
        run_pre_hooks_fn=_noop_pre_hooks,
    )

    assert isinstance(result, BlueprintStageResult)
    assert result.step_obj.id == step_def.id
    assert result.workflow_obj is not None
    assert result.role_block is not None and result.role_block.id == role_blk.id
    assert result.protocol_block is not None and result.protocol_block.id == proto_blk.id
    assert result.execution_persona_block is not None and result.execution_persona_block.id == persona_blk.id
    assert len(result.criteria_blocks_models) == 1
    assert result.criteria_blocks_models[0].id == crit_blk.id
    assert result.output_profile.id == "prf_0195f3a0000070008123456789abcdef"
    assert result.target_locale == "fi"
    assert "Primary source content." in result.global_source_text
    assert result.inputs_payload.raw_inputs == {"doc": "Primary source content."}


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_prompt_block(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify execute_blueprint_and_pre_hooks_stage logs RFC 7807 error and raises on missing prompt blocks."""
    test_logger = logging.getLogger("backend_v2.services.orchestrator.strategies.llm_strategy")
    projector = StateProjector(
        [
            TraceEvent(
                step_name="inputs",
                event_type="input",
                content=ExecutionInputsDTO(raw_inputs={"doc": "Sample text"}),
            )
        ]
    )

    # 1. Missing role_block_id -> ConfigurationError
    step_role = Step(
        id="stp_0195f3a00000700b8000000000000001",
        slug="miss-role",
        name=I18nText(translations={"en": "Miss Role", "fi": "Puuttuva rooli"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LLM,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        cognitive_tier=CognitiveTier.BALANCED,
        role_block_id="blk_0195f3a00000700b8000000000000001",
        extraction_protocol_block_id="blk_0195f3a00000700a8000000000000002",
        criteria_block_ids=["blk_0195f3a0000070008123456789abcdef"],
    )
    in_memory_repo.seed_raw_step(step_role.id, step_role)

    with caplog.at_level(logging.ERROR, logger="backend_v2.services.orchestrator.strategies.llm_strategy"):
        with pytest.raises(ConfigurationError, match="Role Block 'blk_0195f3a00000700b8000000000000001' not found"):
            await execute_blueprint_and_pre_hooks_stage(
                step=StepRule(id="sr_0195f3a0000070008000000000000001", task_blueprint=step_role.id),
                projector=projector,
                context=_create_context(),
                deps=strategy_deps,
                run_pre_hooks_fn=_noop_pre_hooks,
                step_logger=test_logger,
            )

    # 2. Missing extraction_protocol_block_id -> ConfigurationError
    step_proto = step_role.model_copy(
        update={
            "id": "stp_0195f3a00000700b8000000000000002",
            "role_block_id": None,
            "extraction_protocol_block_id": "blk_0195f3a00000700b8000000000000002",
        }
    )
    in_memory_repo.seed_raw_step(step_proto.id, step_proto)
    with pytest.raises(
        ConfigurationError, match="Extraction Protocol Block 'blk_0195f3a00000700b8000000000000002' not found"
    ):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(id="sr_0195f3a0000070008000000000000002", task_blueprint=step_proto.id),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
            step_logger=test_logger,
        )

    # 3. Missing execution_persona_block_id -> ConfigurationError
    step_pers = step_role.model_copy(
        update={
            "id": "stp_0195f3a00000700b8000000000000003",
            "role_block_id": None,
            "execution_persona_block_id": "blk_0195f3a00000700b8000000000000003",
        }
    )
    in_memory_repo.seed_raw_step(step_pers.id, step_pers)
    with pytest.raises(
        ConfigurationError, match="Execution Persona Block 'blk_0195f3a00000700b8000000000000003' not found"
    ):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(id="sr_0195f3a0000070008000000000000003", task_blueprint=step_pers.id),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
            step_logger=test_logger,
        )

    # 4. Missing criteria_block_ids -> AppException (VALIDATION_FAILED)
    step_crit = step_role.model_copy(
        update={
            "id": "stp_0195f3a00000700b8000000000000004",
            "role_block_id": None,
            "criteria_block_ids": ["blk_0195f3a00000700b8000000000000004"],
        }
    )
    in_memory_repo.seed_raw_step(step_crit.id, step_crit)
    with pytest.raises(
        AppException, match="Criteria PromptBlock 'blk_0195f3a00000700b8000000000000004' not found"
    ) as exc_info:
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(id="sr_0195f3a0000070008000000000000004", task_blueprint=step_crit.id),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
            step_logger=test_logger,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_execute_blueprint_stage_error_and_boundary_branches(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify fail-fast error handling and boundary branches in execute_blueprint_and_pre_hooks_stage."""
    projector = StateProjector(
        [
            TraceEvent(
                step_name="inputs",
                event_type="input",
                content=ExecutionInputsDTO(raw_inputs={"doc": "Sample text"}),
            )
        ]
    )

    # 1. Rejects unexpected concurrency kwargs
    invalid_call = functools.partial(execute_blueprint_and_pre_hooks_stage, semaphore=MagicMock())
    with pytest.raises(TypeError):
        await invalid_call(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
            ),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 2. Missing task_blueprint on StepRule
    empty_bp_step = StepRule.model_construct(
        id="sr_0195f3a0000070008123456789abcdef", task_blueprint="", input_mappings={}
    )
    with pytest.raises(AppException, match="has no task_blueprint configured"):
        await execute_blueprint_and_pre_hooks_stage(
            step=empty_bp_step,
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 3. Step blueprint not found in workflow_repo
    with pytest.raises(AppException, match="Step 'stp_0195f3a0000070008000000000099999' not found"):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008000000000099999"
            ),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 4. Missing output_profile_id
    ctx_no_profile = _create_context().model_copy(update={"output_profile_id": ""})
    with pytest.raises(ConfigurationError, match="missing mandatory 'output_profile_id'"):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
            ),
            projector=projector,
            context=ctx_no_profile,
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 5. Missing target_locale
    ctx_no_locale = _create_context().model_copy(update={"target_locale": ""})
    with pytest.raises(ConfigurationError, match="missing mandatory 'target_locale'"):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
            ),
            projector=projector,
            context=ctx_no_locale,
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 6. OutputProfile not found in output_profile_repo
    ctx_bad_profile = _create_context(output_profile_id="prf_0195f3a0000070008000000000099999")
    with pytest.raises(AppException, match="OutputProfile 'prf_0195f3a0000070008000000000099999' not found"):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
            ),
            projector=projector,
            context=ctx_bad_profile,
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

    # 7. Context with explicit prompt_blocks list and mapping global_context_vars
    blk = _create_rule_block("blk_0195f3a0000070008123456789abcdef")
    proto_blk = ProtocolPromptBlock(
        id="blk_0195f3a00000700a8000000000000002",
        slug="proto-blk",
        label=I18nText(translations={"en": "Protocol", "fi": "Protokolla"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        protocol_instructions="Extract exact quotes.",
    )
    ctx_with_blocks = _create_context().model_copy(
        update={
            "prompt_blocks": [blk, proto_blk],
            "global_context_vars": {"language": "fi", "unknown_key": "ignored"},
        }
    )

    async def _mapping_hook_runner(
        step_obj: Step,
        step_rule: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        mutated = hook_state.model_copy(update={"inputs": {"custom_key": "custom_val"}})
        return mutated, []

    res = await execute_blueprint_and_pre_hooks_stage(
        step=StepRule(id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"),
        projector=projector,
        context=ctx_with_blocks,
        deps=strategy_deps,
        run_pre_hooks_fn=_mapping_hook_runner,
    )
    assert res.state_data == {"custom_key": "custom_val"}
    assert res.hook_state.global_context_vars.language == "fi"

    # 7b. Context with empty global_context_vars and hook runner returning inputs=None
    ctx_empty_gvars = _create_context().model_copy(
        update={
            "prompt_blocks": [blk, proto_blk],
            "global_context_vars": None,
        }
    )

    async def _none_inputs_hook_runner(
        step_obj: Step,
        step_rule: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        mutated = hook_state.model_copy(update={"inputs": None})
        return mutated, []

    res_empty = await execute_blueprint_and_pre_hooks_stage(
        step=StepRule(id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"),
        projector=projector,
        context=ctx_empty_gvars,
        deps=strategy_deps,
        run_pre_hooks_fn=_none_inputs_hook_runner,
    )
    assert res_empty.state_data == {}
    assert isinstance(res_empty.hook_state.global_context_vars, GlobalContextVarsDTO)

    # 8. Malformed PromptBlock in DB raises VALIDATION_FAILED
    in_memory_repo.seed_raw_prompt_block(
        "blk_0195f3a00000700b8ad0123456789abc", {"id": "blk_0195f3a00000700b8ad0123456789abc", "category_id": "BAD"}
    )
    with pytest.raises(AppException, match="Malformed PromptBlock in DB"):
        await execute_blueprint_and_pre_hooks_stage(
            step=StepRule(
                id="sr_0195f3a0000070008123456789abcdef", task_blueprint="stp_0195f3a0000070008123456789abcdef"
            ),
            projector=projector,
            context=_create_context(),
            deps=strategy_deps,
            run_pre_hooks_fn=_noop_pre_hooks,
        )

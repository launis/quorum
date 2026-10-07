"""Unit tests for matrix_scoring_hook.

Validates matrix scoring calculations, typed MatrixHookResultDTO container wrapping,
DLQ tolerance, contextual overrides without emojis, and comprehensive Fail-Fast error boundaries.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from pydantic import JsonValue, ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.scoring.matrix_hook import (
    MatrixAggregationStateDTO,
    matrix_scoring_hook,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO
from backend_v2.models.dtos.hook_delta import MatrixHookResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@dataclass(frozen=True)
class MatrixSetupDTO:
    """Strongly typed container for matrix test setup."""

    pb_id: str
    tda_id: str
    step_id: str
    workflow_id: str
    profile_id: str
    execution_id: str
    deps: HookDependencies


def _build_test_matrix_block(pb_id: str, tda_id: str) -> MatrixPromptBlock:
    """Construct a valid MatrixPromptBlock for test fixtures."""
    return MatrixPromptBlock.model_validate(
        {
            "id": pb_id,
            "slug": "test_matrix_block",
            "label": {"translations": {"en": "Leadership Maturity", "fi": "Johtamisen kypsyys"}},
            "description": {"translations": {"en": "Measures leadership behavior", "fi": "Mittaa johtajuutta"}},
            "type": "float",
            "category_id": PromptBlockCategory.MATRIX.value,
            "ai_description": "Assess strategic leadership capabilities.",
            "allow_contextual_override": True,
            "scales": [
                {
                    "score": 1,
                    "ai_label": "Foundational",
                    "claims": [
                        {
                            "label": {"translations": {"en": "Basic alignment", "fi": "Peruslinjaus"}},
                            "tda_assertions": [
                                {
                                    "tda_id": tda_id,
                                    "concept_description": "Demonstrates clear vision alignment.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                }
                            ],
                        }
                    ],
                },
                {
                    "score": 2,
                    "ai_label": "Advanced",
                    "claims": [
                        {
                            "label": {"translations": {"en": "Strategic synthesis", "fi": "Strateginen synteesi"}},
                            "tda_assertions": [
                                {
                                    "tda_id": "tda_99998888777766669999888877776666",
                                    "concept_description": "Synthesizes multi-stakeholder strategy.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                }
                            ],
                        }
                    ],
                },
            ],
        }
    )


def _build_test_step(step_id: str, block_id: str) -> Step:
    """Construct a valid Step containing the matrix block reference."""
    return Step.model_validate(
        {
            "id": step_id,
            "slug": "strategic_matrix_step",
            "name": {"translations": {"en": "Matrix Evaluation Step", "fi": "Matriisiarviointivaihe"}},
            "type": "logic",
            "hook": "matrix_scoring_hook",
            "role_block_id": None,
            "extraction_protocol_block_id": "blk_5555666677778888",
            "criteria_block_ids": [block_id],
        }
    )


def _build_test_workflow(workflow_id: str, profile_id: str) -> Workflow:
    """Construct a valid Workflow."""
    return Workflow.model_validate(
        {
            "id": workflow_id,
            "slug": "executive_review",
            "name": {"translations": {"en": "Executive Review", "fi": "Johdon arviointi"}},
            "description": {"translations": {"en": "Executive review workflow", "fi": "Johdon työnkulku"}},
            "status": "active",
            "version": 1,
            "default_profile_id": profile_id,
            "default_strictness_level": 70,
            "enable_contextual_overrides": True,
            "model_registry_id": "cfg_model_registry_01",
            "historical_context_mode": "DISABLED",
        }
    )


def _build_test_execution(execution_id: str, workflow_id: str, profile_id: str) -> ExecutionRecord:
    """Construct a valid ExecutionRecord."""
    now = datetime.now(timezone.utc)
    return ExecutionRecord.model_validate(
        {
            "id": execution_id,
            "workflow_id": workflow_id,
            "organization_id": "org_1111222233334444",
            "created_by": "usr_1111222233334444",
            "output_profile_id": profile_id,
            "status": "RUNNING",
            "target_locale": "en",
            "created_at": now,
            "updated_at": now,
        }
    )


def _build_test_output_profile(profile_id: str, workflow_id: str, block_id: str) -> OutputProfile:
    """Construct a valid OutputProfile."""
    return OutputProfile.model_validate(
        {
            "id": profile_id,
            "slug": "standard_executive_profile",
            "workflow_id": workflow_id,
            "name": {"translations": {"en": "Standard Executive", "fi": "Vakiojohto"}},
            "matrix_synthesis_groups": [
                {
                    "id": "grp_1111222233334444",
                    "title": {"translations": {"en": "Leadership", "fi": "Johtajuus"}},
                    "target_blocks": [block_id],
                }
            ],
            "display_scale": "original",
        }
    )


@pytest.fixture
def matrix_setup() -> MatrixSetupDTO:
    """Standard fixtures and dependencies for matrix hook tests."""
    pb_id = "blk_1111222233334444"
    tda_id = "tda_11112222333344441111222233334444"
    step_id = "stp_1111222233334444"
    workflow_id = "wf_1111222233334444"
    profile_id = "prof_1111222233334444"
    execution_id = "exe_1111222233334444"

    pb = _build_test_matrix_block(pb_id, tda_id)
    step = _build_test_step(step_id, pb_id)
    wf = _build_test_workflow(workflow_id, profile_id)
    exec_rec = _build_test_execution(execution_id, workflow_id, profile_id)
    profile = _build_test_output_profile(profile_id, workflow_id, pb_id)

    repo = InMemoryUnifiedWorkflowRepository()
    repo._workflows._steps[step_id] = step
    repo._workflows._save_isolated(workflow_id, wf)
    repo._prompt_blocks._save_isolated(pb_id, pb)
    repo._executions._save_isolated(execution_id, exec_rec)
    repo._output_profiles._save_isolated(profile_id, profile)

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    return MatrixSetupDTO(
        pb_id=pb_id,
        tda_id=tda_id,
        step_id=step_id,
        workflow_id=workflow_id,
        profile_id=profile_id,
        execution_id=execution_id,
        deps=deps,
    )


# ==============================================================================
# ISTQB Partition 1: Positive Scenario - Happy Path Execution
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_happy_path_returns_typed_dto(matrix_setup: MatrixSetupDTO) -> None:
    """Positive test: computes matrix scores, returns MatrixHookResultDTO, zero emojis, zero in-place mutations."""
    deps = matrix_setup.deps
    tda_id = matrix_setup.tda_id
    pb_id = matrix_setup.pb_id

    atom_result = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Candidate explicitly demonstrated alignment with vision.",
        source_quote="Our five-year roadmap directly establishes this vision.",
    )

    raw_inputs: dict[str, JsonValue] = {"results": [atom_result]}
    raw_inputs_copy = raw_inputs.copy()

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs=raw_inputs),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)

    # 1. Verify successful result and strongly typed delta
    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MatrixHookResultDTO)

    hook_delta: MatrixHookResultDTO = result.state_delta.delta
    assert pb_id in hook_delta.matrix_outputs
    matrix_output = hook_delta.matrix_outputs[pb_id]
    assert isinstance(matrix_output, LightweightMatrixOutput)
    assert matrix_output.raw_score is not None
    assert matrix_output.raw_score >= 1.0

    # 2. Universal Emoji Eradication verification
    serialized = hook_delta.model_dump_json()
    for emoji_char in ("📍", "💡", "⚠️", "🛠️", "\U0001f4cd", "\U0001f4a1", "\u26a0\ufe0f", "\U0001f6e0\ufe0f"):
        assert emoji_char not in serialized, f"Forbidden emoji '{emoji_char}' found in MatrixHookResultDTO payload!"

    # 3. Verify zero in-place mutation of input dictionary
    assert raw_inputs == raw_inputs_copy


# ==============================================================================
# ISTQB Partition 2: Negative Scenarios - Missing Context & Fail-Fast Gates
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_workflow_repo_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Negative test: missing workflow_repo raises AppException(HOOK_EXECUTION_FAILED)."""
    deps = HookDependencies(
        exec_repo=matrix_setup.deps.exec_repo,
        workflow_repo=None,
        comp_repo=matrix_setup.deps.comp_repo,
        prompt_block_repo=matrix_setup.deps.prompt_block_repo,
        output_profile_repo=matrix_setup.deps.output_profile_repo,
        identity_repo=matrix_setup.deps.identity_repo,
        system_repo=matrix_setup.deps.system_repo,
    )
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.HOOK_EXECUTION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_blueprint_id_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Negative test: missing blueprint_id/step_id raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=None,
        task_blueprint=None,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_not_found_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Negative test: step blueprint not found in repository raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup.deps

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id="stp_0000000000000000",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_results_array_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Negative test: missing 'results' array in inputs raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"other_key": "val"}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_results_not_list_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Negative test: 'results' not a list raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": "not_a_list"}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


# ==============================================================================
# ISTQB Partition 3: DLQ Handling & Tolerance
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_dlq_atom_handling_tolerates_failure(matrix_setup: MatrixSetupDTO) -> None:
    """Negative/Boundary test: atoms with SYSTEM_ERROR/DLQ are counted as DLQ without crashing."""
    deps = matrix_setup.deps
    tda_id = matrix_setup.tda_id
    pb_id = matrix_setup.pb_id

    dlq_atom = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.SYSTEM_ERROR,
        error_details=ErrorDetailsDTO(error_code="LLM_TIMEOUT", message="Inference request timed out after 30s"),
    )

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [dlq_atom]}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MatrixHookResultDTO)
    matrix_output = result.state_delta.delta.matrix_outputs[pb_id]
    assert "[INDETERMINATE]" in matrix_output.justification
    assert matrix_output.raw_score == 1.0
    assert matrix_output.evaluated_atoms[tda_id] == ExecutionStatus.SYSTEM_ERROR


# ==============================================================================
# ISTQB Partition 4: Contextual Override Quote Extraction (Zero Emojis)
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_contextual_override_without_emojis(matrix_setup: MatrixSetupDTO) -> None:
    """Specialized test: contextual override generates pure text quotes without emoji markers."""
    deps = matrix_setup.deps
    tda_id = matrix_setup.tda_id
    pb_id = matrix_setup.pb_id

    override_atom = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        evaluation_reasoning="Implicit alignment verified via cross-departmental initiative context.",
        source_quote=None,
    )

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [override_atom]}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MatrixHookResultDTO)
    hook_delta: MatrixHookResultDTO = result.state_delta.delta
    quotes_list = hook_delta.atom_quotes[pb_id] if pb_id in hook_delta.atom_quotes else []
    assert len(quotes_list) > 0

    # Ensure each quote contains [OVERRIDE] text and ZERO emoji characters
    for quote in quotes_list:
        assert "[OVERRIDE]" in quote.quote
        for emoji in ("📍", "💡", "⚠️", "🛠️"):
            assert emoji not in quote.quote


# ==============================================================================
# ISTQB Partition 5: Advanced Coverage & Error Boundary Partitions
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_no_matrix_blocks_skips(matrix_setup: MatrixSetupDTO) -> None:
    """Step has no criteria block IDs or no matrix blocks; skips scoring gracefully."""
    deps = matrix_setup.deps
    step_without_blocks = _build_test_step(matrix_setup.step_id, "blk_other").model_copy(
        update={"criteria_block_ids": []}
    )
    await deps.workflow_repo.save_step(step_without_blocks)

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_execution_id_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Missing state.execution_id raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    state = HookState(
        execution_id="",
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_execution_not_found_raises(matrix_setup: MatrixSetupDTO) -> None:
    """ExecutionRecord missing from DB raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup.deps

    state = HookState(
        execution_id="exe_0000000000000000",
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_workflow_not_found_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Workflow missing from DB raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup.deps
    await deps.workflow_repo.delete_workflow(matrix_setup.workflow_id)

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id="wf_0000000000000000",
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_output_profile_not_found_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Output profile referenced in execution not found raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup.deps
    await deps.output_profile_repo.delete_output_profile(matrix_setup.profile_id)

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_strictness_level_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Workflow lacking default_strictness_level raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup.deps
    wf_no_strictness = _build_test_workflow(matrix_setup.workflow_id, matrix_setup.profile_id)
    wf_obj = wf_no_strictness.model_copy(update={"default_strictness_level": None})
    await deps.workflow_repo.save_workflow(wf_obj)

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_block_no_scales_raises(matrix_setup: MatrixSetupDTO) -> None:
    """PromptBlock without scales raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup.deps
    pb_no_scales = _build_test_matrix_block(matrix_setup.pb_id, matrix_setup.tda_id)
    pb_obj = pb_no_scales.model_copy(update={"scales": []})
    deps.prompt_block_repo._prompt_blocks._storage[matrix_setup.pb_id] = pb_obj

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_validation_error_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Malformed Step blueprint data raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    deps.workflow_repo._workflows._steps[matrix_setup.step_id] = {"id": "bad_step"}

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_prompt_block_validation_error_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Malformed PromptBlock data raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    deps.prompt_block_repo._prompt_blocks._storage[matrix_setup.pb_id] = {"id": "bad_pb"}

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_evaluation_item_malformed_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Malformed evaluation item that cannot be validated as AtomResultDTO raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    raw_bad_inputs: dict[str, JsonValue] = {"results": [{"invalid_atom": 123}]}
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO.model_construct(raw_inputs=raw_bad_inputs),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_extractive_sensor_and_facts_json_string(matrix_setup: MatrixSetupDTO) -> None:
    """Extractive sensor evaluation track with boolean AST expression and JSON string extracted_facts."""
    deps = matrix_setup.deps
    pb_id = matrix_setup.pb_id
    tda_id = matrix_setup.tda_id

    pb_data = _build_test_matrix_block(pb_id, tda_id)
    scale0 = pb_data.scales[0]
    claim0 = scale0.claims[0]
    assertion0 = claim0.tda_assertions[0].model_copy(
        update={
            "evaluation_track": "EXTRACTIVE_SENSOR",
            "logical_expression": "fact_vision_present",
            "facts_to_find": ["fact_vision_present"],
        }
    )
    claim0 = claim0.model_copy(update={"tda_assertions": [assertion0]})
    scale0 = scale0.model_copy(update={"claims": [claim0]})
    pb_data = pb_data.model_copy(update={"scales": [scale0, pb_data.scales[1]]})
    await deps.prompt_block_repo.update_prompt_block(pb_id, pb_data)

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [],
                "extracted_facts": '{"fact_vision_present": true}',
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MatrixHookResultDTO)
    assert pb_id in result.state_delta.delta.matrix_outputs


@pytest.mark.asyncio
async def test_matrix_scoring_hook_extracted_facts_invalid_json_raises(matrix_setup: MatrixSetupDTO) -> None:
    """Invalid JSON string in extracted_facts raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup.deps
    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [],
                "extracted_facts": "invalid_json{",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_xai_extensions_and_unsupported_extension(matrix_setup: MatrixSetupDTO) -> None:
    """Tests XAI extension parsing and unsupported extension Fail-Fast check."""
    deps = matrix_setup.deps
    pb_id = matrix_setup.pb_id
    tda_id = matrix_setup.tda_id

    # 1. Successful extension extraction
    pb_data = _build_test_matrix_block(pb_id, tda_id)
    prof_data = _build_test_output_profile(matrix_setup.profile_id, matrix_setup.workflow_id, pb_id).model_copy(
        update={"visible_block_extensions": ["coaching"]}
    )
    await deps.prompt_block_repo.update_prompt_block(pb_id, pb_data)
    await deps.output_profile_repo.update_output_profile(matrix_setup.profile_id, prof_data)

    atom_with_ext = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Evaluation complete.",
        source_quote="Verbatim quote",
        extensions={"coaching": "Executive coaching recommendation here."},
    )

    state = HookState(
        execution_id=matrix_setup.execution_id,
        workflow_id=matrix_setup.workflow_id,
        step_id=matrix_setup.step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [atom_with_ext]}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True

    # 2. Unsupported extension triggers Fail-Fast
    pb_data = pb_data.model_copy(update={"output_extensions": ["UNSUPPORTED_EXTENSION_ABC"]})
    await deps.prompt_block_repo.update_prompt_block(pb_id, pb_data)

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_matrix_aggregation_state_dto_validation() -> None:
    """Test positive instantiation and default factories of MatrixAggregationStateDTO."""
    dto = MatrixAggregationStateDTO()
    assert dto.scale_stats == {}
    assert dto.evaluated_atoms == {}
    assert dto.extensions == {}
    assert dto.missing_atoms == []
    assert dto.atom_quotes == []


def test_matrix_aggregation_state_dto_rejects_unknown_attribute() -> None:
    """Test that MatrixAggregationStateDTO rejects undeclared attributes under extra='forbid'."""
    with pytest.raises(ValidationError):
        MatrixAggregationStateDTO.model_validate({"scale_stats": {}, "evaluated_atoms": {}, "extra_key": 123})

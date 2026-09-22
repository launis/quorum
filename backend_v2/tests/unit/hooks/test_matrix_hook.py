"""Unit tests for matrix_scoring_hook.

Validates matrix scoring calculations, typed MatrixHookResultDTO container wrapping,
DLQ tolerance, contextual overrides without emojis, and comprehensive Fail-Fast error boundaries.
"""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.scoring.matrix_hook import matrix_scoring_hook
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO
from backend_v2.models.dtos.hook_delta import MatrixHookResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata


def _build_test_matrix_block(pb_id: str, tda_id: str) -> dict[str, Any]:
    """Construct a valid MatrixPromptBlock dictionary for test fixtures."""
    return {
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
                "score": 1.0,
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
                "score": 2.0,
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


def _build_test_step(step_id: str, block_id: str) -> dict[str, Any]:
    """Construct a valid Step dictionary containing the matrix block reference."""
    return {
        "id": step_id,
        "slug": "strategic_matrix_step",
        "name": {"translations": {"en": "Matrix Evaluation Step", "fi": "Matriisiarviointivaihe"}},
        "type": "logic",
        "hook": "matrix_scoring_hook",
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_5555666677778888",
        "criteria_block_ids": [block_id],
    }


def _build_test_workflow(workflow_id: str, profile_id: str) -> dict[str, Any]:
    """Construct a valid Workflow dictionary."""
    return {
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


def _build_test_execution(execution_id: str, workflow_id: str, profile_id: str) -> dict[str, Any]:
    """Construct a valid ExecutionRecord dictionary."""
    now = datetime.now(timezone.utc).isoformat()
    return {
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


def _build_test_output_profile(profile_id: str, workflow_id: str, block_id: str) -> dict[str, Any]:
    """Construct a valid OutputProfile dictionary."""
    return {
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


@pytest.fixture
def matrix_setup() -> dict[str, Any]:
    """Standard fixtures and dependencies for matrix hook tests."""
    pb_id = "blk_1111222233334444"
    tda_id = "tda_11112222333344441111222233334444"
    step_id = "stp_1111222233334444"
    workflow_id = "wf_1111222233334444"
    profile_id = "prof_1111222233334444"
    execution_id = "exe_1111222233334444"

    pb_dict = _build_test_matrix_block(pb_id, tda_id)
    step_dict = _build_test_step(step_id, pb_id)
    wf_dict = _build_test_workflow(workflow_id, profile_id)
    exec_dict = _build_test_execution(execution_id, workflow_id, profile_id)
    profile_dict = _build_test_output_profile(profile_id, workflow_id, pb_id)

    workflow_repo = AsyncMock()
    workflow_repo.get_step_by_id = AsyncMock(return_value=step_dict)
    workflow_repo.get_workflow_by_id = AsyncMock(return_value=wf_dict)

    prompt_block_repo = AsyncMock()
    prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value=pb_dict)

    exec_repo = AsyncMock()
    exec_repo.get_execution = AsyncMock(return_value=exec_dict)

    output_profile_repo = AsyncMock()
    output_profile_repo.get_output_profile_by_id = AsyncMock(return_value=profile_dict)

    deps = HookDependencies(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    return {
        "pb_id": pb_id,
        "tda_id": tda_id,
        "step_id": step_id,
        "workflow_id": workflow_id,
        "profile_id": profile_id,
        "execution_id": execution_id,
        "deps": deps,
    }


# ==============================================================================
# ISTQB Partition 1: Positive Scenario - Happy Path Execution
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_happy_path_returns_typed_dto(matrix_setup: dict[str, Any]) -> None:
    """Positive test: computes matrix scores, returns MatrixHookResultDTO, zero emojis, zero in-place mutations."""
    deps = matrix_setup["deps"]
    tda_id = matrix_setup["tda_id"]
    pb_id = matrix_setup["pb_id"]

    atom_result = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Candidate explicitly demonstrated alignment with vision.",
        source_quote="Our five-year roadmap directly establishes this vision.",
    )

    raw_inputs: dict[str, Any] = {"results": [atom_result]}
    raw_inputs_copy = raw_inputs.copy()

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
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
async def test_matrix_scoring_hook_missing_workflow_repo_raises(matrix_setup: dict[str, Any]) -> None:
    """Negative test: missing workflow_repo raises AppException(HOOK_EXECUTION_FAILED)."""
    deps = HookDependencies(
        exec_repo=matrix_setup["deps"].exec_repo,
        workflow_repo=None,  # type: ignore[arg-type]
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.HOOK_EXECUTION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_blueprint_id_raises(matrix_setup: dict[str, Any]) -> None:
    """Negative test: missing blueprint_id/step_id raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=None,
        task_blueprint=None,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_not_found_raises(matrix_setup: dict[str, Any]) -> None:
    """Negative test: step blueprint not found in repository raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup["deps"]
    deps.workflow_repo.get_step_by_id = AsyncMock(return_value=None)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id="stp_0000000000000000",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_results_array_raises(matrix_setup: dict[str, Any]) -> None:
    """Negative test: missing 'results' array in inputs raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"other_key": "val"}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_results_not_list_raises(matrix_setup: dict[str, Any]) -> None:
    """Negative test: 'results' not a list raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": "not_a_list"}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


# ==============================================================================
# ISTQB Partition 3: DLQ Handling & Tolerance
# ==============================================================================


@pytest.mark.asyncio
async def test_matrix_scoring_hook_dlq_atom_handling_tolerates_failure(matrix_setup: dict[str, Any]) -> None:
    """Negative/Boundary test: atoms with SYSTEM_ERROR/DLQ are counted as DLQ without crashing."""
    deps = matrix_setup["deps"]
    tda_id = matrix_setup["tda_id"]
    pb_id = matrix_setup["pb_id"]

    dlq_atom = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.SYSTEM_ERROR,
        error_details=ErrorDetailsDTO(error_code="LLM_TIMEOUT", message="Inference request timed out after 30s"),
    )

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
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
async def test_matrix_scoring_hook_contextual_override_without_emojis(matrix_setup: dict[str, Any]) -> None:
    """Specialized test: contextual override generates pure text quotes without emoji markers."""
    deps = matrix_setup["deps"]
    tda_id = matrix_setup["tda_id"]
    pb_id = matrix_setup["pb_id"]

    override_atom = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        evaluation_reasoning="Implicit alignment verified via cross-departmental initiative context.",
        source_quote=None,
    )

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
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
async def test_matrix_scoring_hook_no_matrix_blocks_skips(matrix_setup: dict[str, Any]) -> None:
    """Step has no criteria block IDs or no matrix blocks; skips scoring gracefully."""
    deps = matrix_setup["deps"]
    step_without_blocks = _build_test_step(matrix_setup["step_id"], "blk_other")
    step_without_blocks["criteria_block_ids"] = []
    deps.workflow_repo.get_step_by_id = AsyncMock(return_value=step_without_blocks)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_execution_id_raises(matrix_setup: dict[str, Any]) -> None:
    """Missing state.execution_id raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    state = HookState(
        execution_id="",
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_execution_not_found_raises(matrix_setup: dict[str, Any]) -> None:
    """ExecutionRecord missing from DB raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup["deps"]
    deps.exec_repo.get_execution = AsyncMock(return_value=None)

    state = HookState(
        execution_id="exe_0000000000000000",
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details.get("error_code") == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_workflow_not_found_raises(matrix_setup: dict[str, Any]) -> None:
    """Workflow missing from DB raises AppException(RESOURCE_NOT_FOUND)."""
    deps = matrix_setup["deps"]
    deps.workflow_repo.get_workflow_by_id = AsyncMock(return_value=None)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id="wf_0000000000000000",
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details.get("error_code") == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_output_profile_not_found_raises(matrix_setup: dict[str, Any]) -> None:
    """Output profile referenced in execution not found raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup["deps"]
    deps.output_profile_repo.get_output_profile_by_id = AsyncMock(return_value=None)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_strictness_level_raises(matrix_setup: dict[str, Any]) -> None:
    """Workflow lacking default_strictness_level raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup["deps"]
    wf_no_strictness = _build_test_workflow(matrix_setup["workflow_id"], matrix_setup["profile_id"])
    wf_no_strictness["default_strictness_level"] = None
    wf_obj = Workflow.model_construct(**wf_no_strictness)
    deps.workflow_repo.get_workflow_by_id = AsyncMock(return_value=wf_obj)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_block_no_scales_raises(matrix_setup: dict[str, Any]) -> None:
    """PromptBlock without scales raises AppException(CONFIGURATION_ERROR)."""
    deps = matrix_setup["deps"]
    pb_no_scales = _build_test_matrix_block(matrix_setup["pb_id"], matrix_setup["tda_id"])
    pb_no_scales["scales"] = []
    pb_obj = MatrixPromptBlock.model_construct(**pb_no_scales)
    deps.prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value=pb_obj)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_validation_error_raises(matrix_setup: dict[str, Any]) -> None:
    """Malformed Step blueprint data raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    deps.workflow_repo.get_step_by_id = AsyncMock(return_value={"id": "bad_step"})

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_prompt_block_validation_error_raises(matrix_setup: dict[str, Any]) -> None:
    """Malformed PromptBlock data raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    deps.prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value={"id": "bad_pb"})

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_evaluation_item_malformed_raises(matrix_setup: dict[str, Any]) -> None:
    """Malformed evaluation item that cannot be validated as AtomResultDTO raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    raw_bad_inputs: dict[str, Any] = {"results": [{"invalid_atom": 123}]}
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO.model_construct(raw_inputs=raw_bad_inputs),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_extractive_sensor_and_facts_json_string(matrix_setup: dict[str, Any]) -> None:
    """Extractive sensor evaluation track with boolean AST expression and JSON string extracted_facts."""
    deps = matrix_setup["deps"]
    pb_id = matrix_setup["pb_id"]
    tda_id = matrix_setup["tda_id"]

    pb_data = _build_test_matrix_block(pb_id, tda_id)
    pb_data["scales"][0]["claims"][0]["tda_assertions"][0]["evaluation_track"] = "EXTRACTIVE_SENSOR"
    pb_data["scales"][0]["claims"][0]["tda_assertions"][0]["logical_expression"] = "fact_vision_present"
    pb_data["scales"][0]["claims"][0]["tda_assertions"][0]["facts_to_find"] = ["fact_vision_present"]
    deps.prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value=pb_data)

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
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
async def test_matrix_scoring_hook_extracted_facts_invalid_json_raises(matrix_setup: dict[str, Any]) -> None:
    """Invalid JSON string in extracted_facts raises AppException(VALIDATION_FAILED)."""
    deps = matrix_setup["deps"]
    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
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
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_matrix_scoring_hook_xai_extensions_and_unsupported_extension(matrix_setup: dict[str, Any]) -> None:
    """Tests XAI extension parsing and unsupported extension Fail-Fast check."""
    deps = matrix_setup["deps"]
    pb_id = matrix_setup["pb_id"]
    tda_id = matrix_setup["tda_id"]

    # 1. Successful extension extraction
    pb_data = _build_test_matrix_block(pb_id, tda_id)
    pb_data["output_extensions"] = ["coaching"]
    deps.prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value=pb_data)

    prof_data = _build_test_output_profile(matrix_setup["profile_id"], matrix_setup["workflow_id"], pb_id)
    prof_data["visible_block_extensions"] = ["coaching"]
    deps.output_profile_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)

    atom_with_ext = AtomResultDTO(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Evaluation complete.",
        source_quote="Verbatim quote",
        extensions={"coaching": "Executive coaching recommendation here."},
    )

    state = HookState(
        execution_id=matrix_setup["execution_id"],
        workflow_id=matrix_setup["workflow_id"],
        step_id=matrix_setup["step_id"],
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [atom_with_ext]}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True

    # 2. Unsupported extension triggers Fail-Fast
    pb_data["output_extensions"] = ["UNSUPPORTED_EXTENSION_ABC"]
    deps.prompt_block_repo.get_prompt_block_by_id = AsyncMock(return_value=pb_data)

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value

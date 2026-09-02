"""Unit tests for scoring hooks and matrix calculation engines."""

import hashlib
from collections.abc import Awaitable
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import (
    apply_scoring_logic_hook,
    enforce_passivity_penalty_hook,
    matrix_scoring_hook,
    normalize_matrix_scores_hook,
)
from backend_v2.models.domain.falsifier import FalsifierData, ReasoningFidelity, WaltonStressTest
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO, SecurityCheck
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import (
    EvaluationMandate,
    ExecutionStatus,
    FidelityLevel,
    LaxRiskLevel,
    PromptBlockCategory,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StepOutputDTO


def generate_atom_hash(text: str, mandate: Any = None) -> str:
    """Generates a deterministic atom hash string for tests."""
    return f"tda_{hashlib.md5(text.encode()).hexdigest()[:32]}"


def _build_valid_scale(score: Any, micro_atoms: list[str] | None = None) -> dict[str, Any]:
    """Builds a valid scale dictionary for testing prompt blocks."""
    claims = []
    if micro_atoms is not None:
        claims.append(
            {
                "label": {"translations": {"en": "Test Claim", "fi": "Test Claim"}},
                "tda_assertions": [
                    {
                        "tda_id": f"tda_{hashlib.md5(atom.encode()).hexdigest()[:32]}",
                        "concept_description": f"Concept description for {atom}",
                        "inverse_evidence": False,
                        "aggregation_mode": "EXISTS",
                    }
                    for atom in micro_atoms
                ],
            }
        )
    return {
        "score": score,
        "ai_label": f"Level {score}",
        "claims": claims,
    }


def _build_valid_pb_dict(
    pb_id: str,
    scales: list[dict[str, Any]],
    pb_type: str = "float",
    category_id: str = PromptBlockCategory.MATRIX.value,
) -> dict[str, Any]:
    """Builds a valid prompt block dictionary."""
    pb: dict[str, Any] = {
        "id": pb_id,
        "slug": "test_slug",
        "label": {"translations": {"en": "Test Label", "fi": "Test Label"}},
        "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
        "type": pb_type,
        "category_id": category_id,
    }
    if category_id == PromptBlockCategory.MATRIX.value:
        pb["ai_description"] = "Test AI Desc"
        pb["allow_contextual_override"] = True
    elif category_id in ("execution_persona", "agent_role"):
        pb["role_enforcement"] = "Test Role Enforcement"
    elif category_id == "protocol":
        pb["protocol_instructions"] = "Test Protocol Instructions"
    else:
        pb["instruction_text"] = "Test Instruction Text"
    if scales:
        pb["scales"] = scales
    return pb


def _build_valid_step_dict(prompt_blocks: list[str]) -> dict[str, Any]:
    """Builds a valid step dictionary."""
    return {
        "id": "st_1234567890123456",
        "slug": "test_step",
        "name": {"translations": {"en": "Test Step", "fi": "Test Step"}},
        "type": "logic",
        "hook": "dummy_hook",
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": prompt_blocks,
    }


def _build_valid_execution_dict(execution_id: str, strategy: str = "WATERFALL") -> dict[str, Any]:
    """Builds a valid execution record dictionary."""
    from datetime import datetime, timezone

    return {
        "id": execution_id,
        "workflow_id": "wf_123",
        "organization_id": "org_123",
        "created_by": "usr_123",
        "output_profile_id": "prof_1111111111111111",
        "status": "PENDING",
        "target_locale": "fi",
        "metadata": {},
        "raw_inputs": {},
        "execution_trace": [],
        "step_states": {},
        "frozen_context": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


class MockRepository:
    """Mock repository providing default test step and block data."""

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        """Returns valid step dict."""
        return _build_valid_step_dict(["pb_1234567890123456"])

    async def get_prompt_block_by_id(self, slug: str) -> dict[str, Any]:
        """Returns valid prompt block dict with invalid non-numeric scale."""
        return _build_valid_pb_dict("pb_1234567890123456", [_build_valid_scale("not_a_number")])

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Returns valid execution dict."""
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Returns valid workflow dict."""
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        """Returns valid output profile dict."""
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "WATERFALL",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_0000000000000001",
                    "title": {"translations": {"en": "Default", "fi": "Default"}},
                    "target_blocks": ["*"],
                }
            ],
            "display_scale": "original",
        }


# ==============================================================================
# 1. normalize_matrix_scores_hook tests
# ==============================================================================


@pytest.mark.asyncio
async def test_normalize_matrix_scores_fails_on_corrupt_scale() -> None:
    """Test that setting a corrupted non-float scale in PromptBlocks causes a fail fast AppException."""
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": {
                    "raw_score": 5.0,
                    "normalized_score": 100.0,
                    "justification": "[INITIALIZING]",
                    "evaluated_atoms": {},
                    "extensions": {},
                }
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], normalize_matrix_scores_hook(state, deps))

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Strict Fail-Fast Enforced: Invalid PromptBlock format for 'pb_1234567890123456'" in exc_info.value.message


@pytest.mark.asyncio
async def test_normalize_matrix_scores_tapa_2_string_mapping() -> None:
    """Test that Tapa 2 string PromptBlocks preserve XAI variables in the new LightweightMatrixOutput."""

    class MockRepoTapa2:
        async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
            return _build_valid_step_dict(["tb_1234567890123456"])

        async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
            return _build_valid_pb_dict(
                "tb_1234567890123456",
                [
                    _build_valid_scale(1, ["tapa_atom_1"]),
                    _build_valid_scale(5, ["tapa_atom_5"]),
                ],
            )

        async def get_execution(self, execution_id: str) -> dict[str, Any]:
            return _build_valid_execution_dict(execution_id)

        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wflow_1234567890123456",
                "slug": "test_workflow",
                "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
                "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
                "status": "active",
                "version": 1,
                "default_profile_id": "prof_1111111111111111",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "enable_contextual_overrides": True,
            }

        async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
            return {
                "id": profile_id,
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"translations": {"en": "Test", "fi": "Test"}},
                "strictness_level": 85,
                "scoring_strategy": "WATERFALL",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default", "fi": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
                "display_scale": "original",
            }

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "tb_1234567890123456": {
                    "raw_score": 5.0,
                    "normalized_score": 100.0,
                    "justification": "Tämä on perustelu\n\nKitkaa on",
                    "evaluated_atoms": {},
                    "extensions": {
                        XaiExtensionType.CITATION: "Ote lähteestä",
                        XaiExtensionType.FALSIFICATION: "Vastalause",
                    },
                }
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoTapa2()),
        workflow_repo=cast(Any, MockRepoTapa2()),
        comp_repo=cast(Any, MockRepoTapa2()),
        prompt_block_repo=cast(Any, MockRepoTapa2()),
        output_profile_repo=cast(Any, MockRepoTapa2()),
        identity_repo=cast(Any, MockRepoTapa2()),
        audit_repo=cast(Any, MockRepoTapa2()),
        system_repo=cast(Any, MockRepoTapa2()),
    )

    result = await cast(Awaitable[HookResult], normalize_matrix_scores_hook(state, deps))

    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None

    parsed_output = delta["tb_1234567890123456"]
    extensions = parsed_output["extensions"]

    assert extensions["citation"] == "Ote lähteestä"
    assert extensions["falsification"] == "Vastalause"

    justification = parsed_output["justification"]
    assert "Tämä on perustelu" in justification


@pytest.mark.asyncio
async def test_normalize_matrix_scores_missing_workflow_repo_raises() -> None:
    """Test that normalize_matrix_scores_hook raises HOOK_EXECUTION_FAILED when workflow_repo is missing."""
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, None),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "HOOK_EXECUTION_FAILED"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_step_not_found_raises() -> None:
    """Test that normalize_matrix_scores_hook raises RESOURCE_NOT_FOUND when step is not in database."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = None
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_missing",
        task_blueprint="st_missing",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_missing_prompt_block_raises() -> None:
    """Test that normalize_matrix_scores_hook raises RESOURCE_NOT_FOUND when prompt block is missing."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = None
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": {
                    "raw_score": 3.0,
                    "normalized_score": 50.0,
                    "justification": "J",
                    "evaluated_atoms": {},
                }
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_invalid_input_payload_raises() -> None:
    """Test that normalize_matrix_scores_hook raises VALIDATION_FAILED on invalid matrix input dictionary."""
    mock_workflow = AsyncMock()
    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": "not_a_valid_matrix_dict",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Invalid input for normalization" in exc_info.value.message


@pytest.mark.asyncio
async def test_normalize_matrix_scores_empty_blueprint_raises() -> None:
    """Test that normalize_matrix_scores_hook raises VALIDATION_FAILED when task_blueprint and step_id are empty."""
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="",
        task_blueprint="",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_no_matrix_updates_returns_empty_delta() -> None:
    """Test that normalize_matrix_scores_hook returns empty state_delta when no prompt blocks match."""
    mock_workflow = AsyncMock()
    # Step has criteria block pb_1234567890123456, but raw_inputs does not contain it
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"other_block": 123}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await normalize_matrix_scores_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta == {}


@pytest.mark.asyncio
async def test_normalize_matrix_scores_non_matrix_prompt_block_skipped() -> None:
    """Test that normalize_matrix_scores_hook skips non-matrix prompt blocks."""
    mock_workflow = AsyncMock()
    # PersonaPromptBlock instead of MatrixPromptBlock
    persona_pb = {
        "id": "pb_1234567890123456",
        "slug": "persona_slug",
        "label": {"translations": {"en": "Persona", "fi": "Persona"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "category_id": PromptBlockCategory.EXECUTION_PERSONA.value,
        "type": "string",
    }
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = persona_pb

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": {"some": "data"},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await normalize_matrix_scores_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta == {}


@pytest.mark.asyncio
async def test_normalize_matrix_scores_step_validation_error_raises() -> None:
    """Test that normalize_matrix_scores_hook raises VALIDATION_FAILED when Step model validation fails."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = {"invalid": "schema"}
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="st_invalid",
        task_blueprint="st_invalid",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_recalculate_invalid_lightweight_matrix_raises() -> None:
    """Test recalculate helper raises VALIDATION_FAILED when matrix payload is malformed."""
    from backend_v2.hooks.scoring.normalization_hook import recalculate

    scales = [_build_valid_scale(1, ["atom_1"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)

    payload: dict[str, Any] = {
        "pb_1234567890123456": {
            "evaluated_atoms": {"atom_1": "PASSED"},
            "justification": "some text",
            "raw_score": "not_a_float",
        }
    }

    mock_workflow = AsyncMock()
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 85,
        "scoring_strategy": "WATERFALL",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default", "fi": "Default"}},
                "target_blocks": ["*"],
            }
        ],
        "display_scale": "original",
    }

    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await recalculate(payload, "prof_1111111111111111", deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_normalize_matrix_scores_recalculate_success() -> None:
    """Test recalculate helper function in normalization_hook with valid atoms and profiles."""
    from backend_v2.hooks.scoring.normalization_hook import recalculate

    scales = [
        _build_valid_scale(1, ["atom_1"]),
        _build_valid_scale(2, ["atom_2"]),
        _build_valid_scale(3, ["atom_3"]),
        _build_valid_scale(4, ["atom_4"]),
        _build_valid_scale(5, ["atom_5"]),
    ]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    # Add valid output extensions
    pb_dict["output_extensions"] = ["citation", "falsification"]

    atom_1_id = f"tda_{hashlib.md5(b'atom_1').hexdigest()[:32]}"
    atom_5_id = f"tda_{hashlib.md5(b'atom_5').hexdigest()[:32]}"

    matrix_dto = LightweightMatrixOutput(
        raw_score=5.0,
        normalized_score=100.0,
        justification="Evaluation text",
        evaluated_atoms={atom_1_id: ExecutionStatus.PASSED, atom_5_id: ExecutionStatus.FAILED},
        extensions={},
    )

    payload: dict[str, Any] = {
        "pb_1234567890123456": matrix_dto.model_dump(mode="json"),
    }

    mock_repo = MockRepoWaterfall()
    mock_repo.pb_id = "pb_1234567890123456"
    # Ensure prompt block repo returns pb_dict
    mock_workflow = AsyncMock()
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 85,
        "scoring_strategy": "WATERFALL",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default", "fi": "Default"}},
                "target_blocks": ["*"],
            }
        ],
        "display_scale": "original",
    }

    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    await recalculate(payload, "prof_1111111111111111", deps)
    assert "true_atoms_count" in payload
    assert "false_atoms_count" in payload
    assert payload["true_atoms_count"] == 1
    assert payload["false_atoms_count"] == 1


@pytest.mark.asyncio
async def test_recalculate_unsupported_xai_extension_raises() -> None:
    """Test recalculate raises VALIDATION_FAILED when prompt block contains unsupported XAI extension."""
    from backend_v2.hooks.scoring.normalization_hook import recalculate

    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    pb_dict["output_extensions"] = ["totally_invalid_extension_type"]

    atom_1_id = f"tda_{hashlib.md5(b'atom_1').hexdigest()[:32]}"
    matrix_dto = LightweightMatrixOutput(
        raw_score=1.0,
        normalized_score=0.0,
        justification="Evaluation text",
        evaluated_atoms={atom_1_id: ExecutionStatus.PASSED},
        extensions={},
    )

    payload: dict[str, Any] = {
        "pb_1234567890123456": matrix_dto.model_dump(mode="json"),
    }

    mock_workflow = AsyncMock()
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 85,
        "scoring_strategy": "WATERFALL",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default", "fi": "Default"}},
                "target_blocks": ["*"],
            }
        ],
        "display_scale": "original",
    }

    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await recalculate(payload, "prof_1111111111111111", deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_recalculate_none_profile_returns_early() -> None:
    """Test that recalculate returns early when profile_id is None."""
    from backend_v2.hooks.scoring.normalization_hook import recalculate

    payload: dict[str, Any] = {"pb_1": 123}
    mock_workflow = AsyncMock()
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    await recalculate(payload, None, deps)
    assert payload == {"pb_1": 123}


# ==============================================================================
# 2. matrix_scoring_hook tests
# ==============================================================================


class MockRepoWaterfall:
    """Mock repository for waterfall scoring tests."""

    def __init__(self, pb_id: str = "pb_1234567890123456") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        """Returns step with matrix prompt block."""
        return _build_valid_step_dict([self.pb_id])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        """Returns 5-level matrix prompt block."""
        return _build_valid_pb_dict(
            self.pb_id,
            [
                _build_valid_scale(1, ["atom_1"]),
                _build_valid_scale(2, ["atom_2"]),
                _build_valid_scale(3, ["atom_3"]),
                _build_valid_scale(4, ["atom_4"]),
                _build_valid_scale(5, ["atom_5"]),
            ],
        )

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Returns valid execution dict."""
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Returns valid workflow dict."""
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        """Returns valid output profile."""
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "WATERFALL",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_0000000000000001",
                    "title": {"translations": {"en": "Default", "fi": "Default"}},
                    "target_blocks": ["*"],
                }
            ],
            "display_scale": "original",
        }


class MockRepoWaterfallMixed:
    """Mock repository with mixed matrix and instruction blocks."""

    def __init__(self) -> None:
        self.pb_matrix = "pm_1234567890123456"
        self.pb_instruction = "pi_1234567890123456"

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        """Returns step with mixed prompt blocks."""
        return _build_valid_step_dict([self.pb_matrix, self.pb_instruction])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        """Returns prompt block based on ID."""
        if pb_id == self.pb_matrix:
            return _build_valid_pb_dict(
                self.pb_matrix,
                [
                    _build_valid_scale(1, ["atom_1"]),
                    _build_valid_scale(5, ["atom_5"]),
                ],
            )
        else:
            return _build_valid_pb_dict(self.pb_instruction, [], pb_type="instruction", category_id="system_rule")

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Returns execution dict."""
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Returns workflow dict."""
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        """Returns output profile dict."""
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "WATERFALL",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_0000000000000001",
                    "title": {"translations": {"en": "Default", "fi": "Default"}},
                    "target_blocks": ["*"],
                }
            ],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_validation_failure_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when step fails Pydantic validation."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = {"invalid": "step"}
    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="st_invalid",
        task_blueprint="st_invalid",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_prompt_block_validation_failure_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when prompt block fails Pydantic validation."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = {"invalid": "prompt_block"}
    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_execution_id_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when execution_id is empty."""
    mock_workflow = MockRepoWaterfall()
    state = HookState(
        execution_id="",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_workflow_repo_raises() -> None:
    """Test that matrix_scoring_hook raises HOOK_EXECUTION_FAILED when workflow_repo is missing."""
    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, None),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "HOOK_EXECUTION_FAILED"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_empty_blueprint_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when blueprint is empty."""
    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="",
        task_blueprint="",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_step_not_found_raises() -> None:
    """Test that matrix_scoring_hook raises RESOURCE_NOT_FOUND when step is not in database."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = None
    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="st_missing",
        task_blueprint="st_missing",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_no_matrix_blocks_skips() -> None:
    """Test that matrix_scoring_hook returns empty HookResult if step has no matrix blocks."""
    mock_workflow = AsyncMock()
    persona_pb = {
        "id": "pb_1234567890123456",
        "slug": "persona_slug",
        "label": {"translations": {"en": "Persona", "fi": "Persona"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "category_id": PromptBlockCategory.EXECUTION_PERSONA.value,
        "type": "string",
    }
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = persona_pb

    state = HookState(
        execution_id="ex_1",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta == {}


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_workflow_raises() -> None:
    """Test that matrix_scoring_hook raises RESOURCE_NOT_FOUND when workflow is missing."""
    mock_workflow = AsyncMock()
    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_execution.return_value = _build_valid_execution_dict("ex_1234567890abcdef")
    mock_workflow.get_workflow_by_id.return_value = None

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_profile_config_raises() -> None:
    """Test that matrix_scoring_hook raises CONFIGURATION_ERROR when output profile is missing scoring configuration."""
    mock_workflow = AsyncMock()
    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_execution.return_value = _build_valid_execution_dict("ex_1234567890abcdef")
    mock_workflow.get_workflow_by_id.return_value = {
        "id": "wflow_1234567890123456",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
        "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "enable_contextual_overrides": True,
    }
    mock_workflow.get_output_profile_by_id.return_value = None

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "CONFIGURATION_ERROR"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_execution_raises() -> None:
    """Test that matrix_scoring_hook raises RESOURCE_NOT_FOUND when execution record is missing."""
    mock_workflow = AsyncMock()
    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict("pb_1234567890123456", scales=scales)
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_execution.return_value = None

    state = HookState(
        execution_id="ex_missing",
        workflow_id="wf1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_results_array_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when 'results' is missing in state.inputs."""
    mock_workflow = MockRepoWaterfall()
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"missing_results": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "'results' array is completely missing" in exc_info.value.message


@pytest.mark.asyncio
async def test_matrix_scoring_hook_invalid_extracted_facts_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when extracted_facts is not a dictionary."""
    mock_workflow = MockRepoWaterfall()
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [],
                "extracted_facts": "invalid_not_a_dict",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "extracted_facts must be a dictionary" in exc_info.value.message


@pytest.mark.asyncio
async def test_matrix_scoring_hook_evaluations_not_list_raises() -> None:
    """Test that matrix_scoring_hook raises VALIDATION_FAILED when results is not a list."""
    mock_workflow = MockRepoWaterfall()
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": "not_a_list",
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await matrix_scoring_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "'evaluations' array is not a list" in exc_info.value.message


@pytest.mark.asyncio
async def test_matrix_scoring_hook_ignores_instructions() -> None:
    """Test that waterfall scoring gracefully skips instructional PromptBlocks without crashing."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [
                    {
                        "tda_id": atom_hash,
                        "status": ExecutionStatus.PASSED,
                        "evaluation_reasoning": "Valid reasoning",
                        "source_quote": "mock quote",
                        "contextual_override": False,
                    }
                ],
                "extracted_facts": {},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallMixed()),
        workflow_repo=cast(Any, MockRepoWaterfallMixed()),
        comp_repo=cast(Any, MockRepoWaterfallMixed()),
        prompt_block_repo=cast(Any, MockRepoWaterfallMixed()),
        output_profile_repo=cast(Any, MockRepoWaterfallMixed()),
        identity_repo=cast(Any, MockRepoWaterfallMixed()),
        audit_repo=cast(Any, MockRepoWaterfallMixed()),
        system_repo=cast(Any, MockRepoWaterfallMixed()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_pass_all() -> None:
    """Test standard hybrid model when everything passes."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        evaluations.append(
            {
                "tda_id": atom_hash,
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert delta["pb_1234567890123456"]["raw_score"] == 5.0
    assert delta["pb_1234567890123456"]["justification"] == "[INITIALIZING]"
    assert delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_waterfall_engine_breakdown"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_ceiling_cap() -> None:
    """Test that the waterfall ceiling caps the final score despite high weighted score."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Level 1: 1/1 (ok), Level 2: 0/1 (fails), Level 3, 4, 5: 1/1 (ok)
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = True if i != 2 else False
        evaluation: dict[str, Any] = {
            "tda_id": atom_hash,
            "status": ExecutionStatus.PASSED if is_hit else ExecutionStatus.FAILED,
            "evaluation_reasoning": "Hyväksytty" if is_hit else "Hylätty",
            "contextual_override": False,
        }
        if is_hit:
            evaluation["source_quote"] = "mock quote"
        evaluations.append(evaluation)

    state = HookState(
        execution_id="ex_2222222222222222",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None

    assert abs(delta["pb_1234567890123456"]["raw_score"] - 1.3) < 0.01


@pytest.mark.asyncio
async def test_matrix_scoring_hook_graceful_missing() -> None:
    """Test missing context formatting logic."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Fail level 3
    for i in range(1, 4):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = False if i == 3 else True
        reasoning = "Testivaste" if not is_hit else "OK"
        evaluations.append(
            {
                "tda_id": atom_hash,
                "status": ExecutionStatus.PASSED if is_hit else "FAIL",
                "evaluation_reasoning": reasoning,
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[Any], matrix_scoring_hook(state, deps))

    assert "Strict Fail-Fast" in str(exc_info.value)


class MockRepoWaterfallSimulation:
    """Mock repository for full simulation test."""

    def __init__(self, pb_id: str = "pb_1234567890123456") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        """Returns valid step dict."""
        return _build_valid_step_dict([self.pb_id])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        """Returns 5-level matrix block with multiple atoms per level."""
        return _build_valid_pb_dict(
            self.pb_id,
            [
                _build_valid_scale(1, ["L1_A1", "L1_A2"]),
                _build_valid_scale(2, ["L2_A1", "L2_A2"]),
                _build_valid_scale(3, ["L3_A1", "L3_A2"]),
                _build_valid_scale(4, ["L4_A1"]),
                _build_valid_scale(5, ["L5_A1"]),
            ],
        )

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Returns valid execution dict."""
        return _build_valid_execution_dict(execution_id, strategy="AVERAGE")

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Returns valid workflow dict."""
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        """Returns valid output profile dict with AVERAGE strategy."""
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "AVERAGE",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_0000000000000001",
                    "title": {"translations": {"en": "Default", "fi": "Default"}},
                    "target_blocks": ["*"],
                }
            ],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_matrix_scoring_hook_full_simulation() -> None:
    """Simulates a complex real-world evaluation trace to ensure mathematical perfection."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = [
        {
            "tda_id": generate_atom_hash("L1_A1", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L1_A2", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L2_A1", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L2_A2", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L3_A1", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L3_A2", mandate),
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Aihetodistetta EI esitetty.",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L4_A1", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Hieno oivallus!",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "tda_id": generate_atom_hash("L5_A1", mandate),
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Ei yltänyt tälle tasolle.",
            "contextual_override": False,
        },
    ]

    state = HookState(
        execution_id="ex_9999999999999999",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallSimulation()),
        workflow_repo=cast(Any, MockRepoWaterfallSimulation()),
        comp_repo=cast(Any, MockRepoWaterfallSimulation()),
        prompt_block_repo=cast(Any, MockRepoWaterfallSimulation()),
        output_profile_repo=cast(Any, MockRepoWaterfallSimulation()),
        identity_repo=cast(Any, MockRepoWaterfallSimulation()),
        audit_repo=cast(Any, MockRepoWaterfallSimulation()),
        system_repo=cast(Any, MockRepoWaterfallSimulation()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert delta["pb_1234567890123456"]["raw_score"] > 1.0
    assert delta["pb_1234567890123456"]["justification"] == "[INITIALIZING]"
    assert delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_pure_average_engine_breakdown"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_status_key() -> None:
    """Test that matrix_scoring_hook operates robustly even when evaluations omit the 'status' key."""
    evaluations: list[dict[str, Any]] = [
        {
            "evaluation_reasoning": "Valid analytical statement",
            "source_quote": "mock quote",
            "contextual_override": False,
        },
        {
            "_dlq_status": "FAILED/DLQ",
            "reason": "Simulated pipeline timeout",
        },
    ]

    state = HookState(
        execution_id="exe_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[Any], matrix_scoring_hook(state, deps))

    assert "Strict Fail-Fast" in str(exc_info.value)


@pytest.mark.asyncio
async def test_matrix_scoring_hook_contextual_override() -> None:
    """Test that contextual_override correctly treats a missing quote as PASSED/TRUE without penalty."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Total 5 atoms: 4 PASS, 1 OVERRIDE (acts as PASS)
    for i in range(1, 5):
        evaluations.append(
            {
                "tda_id": generate_atom_hash(f"atom_{i}", mandate),
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )
    evaluations.append(
        {
            "tda_id": generate_atom_hash("atom_5", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Overridden correctly",
            "source_quote": None,
            "contextual_override": True,
        }
    )

    state = HookState(
        execution_id="exec_0123456789abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None

    raw_score = delta["pb_1234567890123456"]["raw_score"]
    assert abs(raw_score - 5.0) < 0.01


@pytest.mark.asyncio
async def test_matrix_scoring_hook_quote_evidence_crash() -> None:
    """Test to verify QuoteEvidenceDTO handling when status is FAILED."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    evaluations = [
        {
            "tda_id": atom_hash,
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Hylätty",
            "source_quote": None,
            "contextual_override": False,
        }
    ]

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_empty_evaluations() -> None:
    """Test that matrix_scoring_hook handles empty evaluations list properly."""
    pb = _build_valid_pb_dict("blk_1111111111111111", [_build_valid_scale(1, ["atom_test"])])
    state = HookState(
        inputs=ExecutionInputsDTO(raw_inputs={"results": [], "extracted_facts": {}, "execution_metadata": {}}),
        step_id="sp_empty_evals",
        execution_id="exe_1111111111111111",
        workflow_id="wf_1",
        task_blueprint="sp_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(
            vars={
                "matrix_blocks": [("blk_1111111111111111", MatrixPromptBlock(**pb))],
                "scoring_profile": {"id": "prof_1", "scoring_strategy": "baseline", "strictness_level": "normal"},
            }
        ),
    )

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result is not None
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert delta["results"] == []


@pytest.mark.asyncio
async def test_matrix_scoring_hook_cognitive_dlq_status() -> None:
    """Test matrix_scoring_hook handles cognitive DLQ status appropriately."""
    mock_workflow = MockRepoWaterfall()
    atom_hash = generate_atom_hash("atom_1", EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value)

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [
                    {
                        "tda_id": atom_hash,
                        "status": ExecutionStatus.SYSTEM_ERROR,
                        "evaluation_reasoning": "DLQ reasoning",
                        "source_quote": "mock quote",
                        "contextual_override": False,
                        "error_details": {"error_code": "LLM_TIMEOUT", "message": "Request timed out"},
                    }
                ],
                "extracted_facts": {},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_override_disabled_returns_false() -> None:
    """Test matrix_scoring_hook rejects contextual_override when workflow has enable_contextual_overrides=False."""
    mock_workflow = AsyncMock()
    pb_id = "pb_1234567890123456"
    atom_hash = generate_atom_hash("atom_1", EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value)
    scales = [_build_valid_scale(1, ["atom_1"]), _build_valid_scale(5, ["atom_5"])]
    pb_dict = _build_valid_pb_dict(pb_id, scales=scales)
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict([pb_id])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_execution.return_value = _build_valid_execution_dict("ex_1111222233334444")
    mock_workflow.get_workflow_by_id.return_value = {
        "id": "wflow_1234567890123456",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
        "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "enable_contextual_overrides": False,
    }
    mock_workflow.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 85,
        "scoring_strategy": "WATERFALL",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default", "fi": "Default"}},
                "target_blocks": ["*"],
            }
        ],
        "display_scale": "original",
    }

    state = HookState(
        execution_id="ex_1111222233334444",
        workflow_id="wf_123",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [
                    {
                        "tda_id": atom_hash,
                        "status": ExecutionStatus.PASSED,
                        "evaluation_reasoning": "Override attempted",
                        "source_quote": None,
                        "contextual_override": True,
                    }
                ],
                "extracted_facts": {},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_matrix_id_filtering() -> None:
    """Test matrix_scoring_hook filters out evaluations belonging to another matrix_id."""
    mock_workflow = MockRepoWaterfall()
    atom_hash = generate_atom_hash("atom_1", EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value)

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [
                    {
                        "tda_id": atom_hash,
                        "matrix_id": "pb_other_matrix_1111",
                        "status": ExecutionStatus.PASSED,
                        "evaluation_reasoning": "Belongs to other matrix",
                        "source_quote": "mock quote",
                        "contextual_override": False,
                    }
                ],
                "extracted_facts": {},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_extractive_sensor_and_dlq() -> None:
    """Test matrix_scoring_hook evaluates EXTRACTIVE_SENSOR assertions and records DLQ outcomes."""
    mock_workflow = AsyncMock()
    pb_id = "pb_1234567890123456"
    tda_sensor_id = f"tda_{hashlib.md5(b'sensor_atom_1').hexdigest()[:32]}"
    tda_dlq_id = f"tda_{hashlib.md5(b'cognitive_dlq_1').hexdigest()[:32]}"

    tda_assertion = {
        "tda_id": tda_sensor_id,
        "concept_description": "Extractive sensor concept description for testing",
        "aggregation_mode": "EXISTS",
        "inverse_evidence": False,
        "evaluation_track": "EXTRACTIVE_SENSOR",
        "facts_to_find": ["fact_1"],
        "logical_expression": "fact_1",
    }
    tda_dlq = {
        "tda_id": tda_dlq_id,
        "concept_description": "Cognitive DLQ concept description for testing",
        "aggregation_mode": "EXISTS",
        "inverse_evidence": False,
        "evaluation_track": "COGNITIVE_JUDGEMENT",
        "logical_expression": None,
    }
    scale_1 = {
        "score": 1,
        "ai_label": "Level 1",
        "claims": [
            {
                "label": {"translations": {"en": "Claim 1", "fi": "Claim 1"}},
                "tda_assertions": [tda_assertion, tda_dlq],
            }
        ],
    }
    scale_5 = {
        "score": 5,
        "ai_label": "Level 5",
        "claims": [
            {
                "label": {"translations": {"en": "Claim 5", "fi": "Claim 5"}},
                "tda_assertions": [
                    {
                        "tda_id": f"tda_{hashlib.md5(b'scale_5_atom').hexdigest()[:32]}",
                        "concept_description": "Scale 5 atom concept description for testing",
                        "aggregation_mode": "EXISTS",
                        "inverse_evidence": False,
                    }
                ],
            }
        ],
    }
    pb_dict = _build_valid_pb_dict(pb_id, scales=[scale_1, scale_5])
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict([pb_id])
    mock_workflow.get_prompt_block_by_id.return_value = pb_dict
    mock_workflow.get_execution.return_value = _build_valid_execution_dict("ex_1111222233334444")
    mock_workflow.get_workflow_by_id.return_value = {
        "id": "wflow_1234567890123456",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
        "description": {"translations": {"en": "Test Desc", "fi": "Test Desc"}},
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "enable_contextual_overrides": True,
    }
    mock_workflow.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 85,
        "scoring_strategy": "WATERFALL",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default", "fi": "Default"}},
                "target_blocks": ["*"],
            }
        ],
        "display_scale": "original",
    }

    state = HookState(
        execution_id="ex_1111222233334444",
        workflow_id="wf_123",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [
                    {
                        "tda_id": tda_dlq_id,
                        "status": ExecutionStatus.SYSTEM_ERROR,
                        "evaluation_reasoning": "Infra failure",
                        "source_quote": "some quote",
                        "_dlq_status": "FAILED/DLQ",
                    }
                ],
                "extracted_facts": {"fact_1": True},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert pb_id in result.state_delta.delta


@pytest.mark.asyncio
async def test_matrix_scoring_hook_propagates_extensions() -> None:
    """Test that matrix_scoring_hook aggregates atom-level extensions into the Matrix output."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    evaluations = [
        {
            "tda_id": atom_hash,
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Missing requirement",
            "source_quote": None,
            "contextual_override": False,
            "extensions": {"coaching": "This is a coaching tip."},
        }
    ]

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": ["coaching", "falsification", "remediation_steps"],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default", "fi": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "pb_1234567890123456" in delta
    matrix_output = delta["pb_1234567890123456"]
    assert matrix_output is not None

    extensions = matrix_output["extensions"]
    assert "coaching" in extensions
    assert extensions["coaching"] == "This is a coaching tip."


@pytest.mark.xfail(reason="Phase 2 pending: MatrixDomainParser evaluates Enum as truthy")
@pytest.mark.asyncio
async def test_scoring_matrix_namespace_isolation() -> None:
    """Test that Matrix B evaluations leaking into Matrix A's loop are ignored."""
    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_1", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": "pb_OTHER_MATRIX",
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Reason",
        "source_quote": "mock quote",
        "contextual_override": False,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [ev_dict], "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default", "fi": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "pb_1234567890123456" in delta
    matrix_output = delta["pb_1234567890123456"]
    assert matrix_output["evaluated_atoms"][atom_hash] == ExecutionStatus.FAILED
    assert matrix_output["raw_score"] == 1.0


@pytest.mark.xfail(reason="Phase 2 pending: MatrixDomainParser evaluates Enum as truthy")
@pytest.mark.asyncio
async def test_scoring_regular_tda_path_bypasses_namespace_check() -> None:
    """Test that Regular TDA evaluations (matrix_id=None) bypass the namespace check."""
    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_3", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": None,
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Reason",
        "source_quote": "mock quote",
        "contextual_override": False,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [ev_dict], "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default", "fi": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "pb_1234567890123456" in delta
    matrix_output = delta["pb_1234567890123456"]
    assert atom_hash in matrix_output["evaluated_atoms"]
    assert matrix_output["evaluated_atoms"][atom_hash] == ExecutionStatus.PASSED


@pytest.mark.xfail(reason="Phase 2 pending: MatrixDomainParser evaluates Enum as truthy")
@pytest.mark.asyncio
async def test_failed_atom_with_override_does_not_inflate_score() -> None:
    """Test that a FAILED atom with contextual_override=True does NOT inflate the matrix score."""
    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_3", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": "pb_1234567890123456",
        "status": ExecutionStatus.FAILED,
        "evaluation_reasoning": "Failed reason",
        "source_quote": None,
        "contextual_override": True,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": [ev_dict], "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000001",
                        "title": {"translations": {"en": "Default", "fi": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "pb_1234567890123456" in delta
    matrix_output = delta["pb_1234567890123456"]
    assert matrix_output["evaluated_atoms"][atom_hash] == ExecutionStatus.FAILED


class MockRepoWaterfallStrict(MockRepoWaterfall):
    """Mock repository with contextual override disabled on prompt block."""

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        """Returns prompt block with allow_contextual_override=False."""
        pb = await super().get_prompt_block_by_id(pb_id)
        pb["allow_contextual_override"] = False
        return pb


@pytest.mark.xfail(reason="Phase 2 pending: MatrixDomainParser evaluates Enum as truthy")
@pytest.mark.asyncio
async def test_matrix_scoring_hook_illegal_override_penalty() -> None:
    """Test that illegal contextual_override maps to FALSE when allow_contextual_override is False."""
    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Total 5 atoms, 1 illegal override, 4 PASS
    for i in range(1, 5):
        evaluations.append(
            {
                "tda_id": generate_atom_hash(f"atom_{i}", mandate),
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )
    evaluations.append(
        {
            "tda_id": generate_atom_hash("atom_5", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Contested",
            "source_quote": "mock quote",
            "contextual_override": True,
        }
    )

    state = HookState(
        execution_id="exec_0123456789abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations, "extracted_facts": {}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallStrict()),
        workflow_repo=cast(Any, MockRepoWaterfallStrict()),
        comp_repo=cast(Any, MockRepoWaterfallStrict()),
        prompt_block_repo=cast(Any, MockRepoWaterfallStrict()),
        output_profile_repo=cast(Any, MockRepoWaterfallStrict()),
        identity_repo=cast(Any, MockRepoWaterfallStrict()),
        audit_repo=cast(Any, MockRepoWaterfallStrict()),
        system_repo=cast(Any, MockRepoWaterfallStrict()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None

    raw_score = delta["pb_1234567890123456"]["raw_score"]
    assert abs(raw_score - 4.0) < 0.01


@pytest.mark.asyncio
async def test_phase_1_5_negative_raw_boolean_crashes_validation() -> None:
    """Verify that passing raw boolean values or strings to evaluated_atoms crashes Pydantic validation."""
    from pydantic import ValidationError

    from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO

    with pytest.raises(ValidationError):
        TraceMatrixPayloadDTO.model_validate(
            {"matrix_id": "pb_123", "evaluated_atoms": {"tda_1": True}, "atom_quotes": {}}
        )

    with pytest.raises(ValidationError):
        TraceMatrixPayloadDTO.model_validate(
            {"matrix_id": "pb_123", "evaluated_atoms": {"tda_1": "FAILED"}, "atom_quotes": {}}
        )


# ==============================================================================
# 3. apply_scoring_logic_hook tests
# ==============================================================================


def test_apply_scoring_logic_hook_success() -> None:
    """Test that apply_scoring_logic_hook computes commensurate average score correctly without penalties."""
    eval_matrices = {"blk_1": 80.0, "blk_2": 90.0}
    state = HookState(
        execution_id="exec_0000000000000001",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"steps": [], "inputs": {"_evaluative_matrices": eval_matrices}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    result = apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "scoring_result" in delta
    scoring_result = delta["scoring_result"]
    assert scoring_result["total_score"] == 85.0
    assert scoring_result["final_score"] == 85.0
    assert scoring_result["penalties_applied"] == []
    assert scoring_result["aggregation_status"] == "V2 Commensurate Average of 2 matrices"


def test_apply_scoring_logic_hook_with_hoisted_step_output_dto() -> None:
    """Test that apply_scoring_logic_hook extracts evaluative matrices from hoisted StepOutputDTO list."""
    step_output = StepOutputDTO(
        step_id="st_matrix",
        block_id="_evaluative_matrices",
        data_type="matrix",
        payload={"blk_1": 70.0, "blk_2": 90.0},
    )
    state = HookState(
        execution_id="exec_0000000000000002",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"steps": [step_output.model_dump(mode="json")]}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    result = apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    scoring_result = delta["scoring_result"]
    assert scoring_result["final_score"] == 80.0


def test_apply_scoring_logic_hook_with_security_and_falsifier_penalties(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that apply_scoring_logic_hook applies security and post-hoc penalties."""
    from backend_v2.settings import get_settings

    current_settings = get_settings()
    mock_settings = current_settings.model_copy(
        update={"scoring_security_penalty": 0.2, "scoring_post_hoc_penalty": 0.2}
    )
    monkeypatch.setattr("backend_v2.hooks.scoring.falsifier_hook.get_settings", lambda: mock_settings)
    sec_dto = InputProcessingOutputDTO(
        thought_process="Analyzing input for injection threats",
        conclusion="Threat detected in user input",
        confidence_score=0.95,
        is_safe=False,
        rejection_reason="Threat detected",
        security_check=SecurityCheck(
            threat_detected=True,
            risk_level=LaxRiskLevel.HIGH,
            risk_score=3.0,
            simulation_score=1.0,
            anonymized=False,
            pii_findings=[],
        ),
    )
    falsifier_dto = FalsifierData(
        stress_test_findings=[
            WaltonStressTest(
                question="Is the reasoning post-hoc?",
                evidence_held=False,
                observation="Post-hoc rationalization detected",
            )
        ],
        fidelity_audit=ReasoningFidelity(
            fidelity_score=FidelityLevel.WEAK,
            fidelity_numeric=1.0,
            abductive_score=1.0,
            plausibility_score=1.0,
            justification="Post-hoc reasoning detected",
            post_hoc_rationalization=True,
        ),
    )

    step_falsifier_dto = StepFalsifierDTO(
        thought_process="Auditing reasoning fidelity",
        conclusion="Post-hoc rationalization identified",
        confidence_score=0.9,
        falsifier_data=falsifier_dto,
    )

    eval_matrices = {"blk_1": 100.0}
    inputs: dict[str, Any] = {
        "steps": [],
        "inputs": {
            "_evaluative_matrices": eval_matrices,
            "step_input_processing": sec_dto.model_dump(mode="json"),
            "step_falsifier": step_falsifier_dto.model_dump(mode="json"),
        },
    }

    state = HookState(
        execution_id="exec_0000000000000003",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs=inputs),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    result = apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    scoring_result = delta["scoring_result"]
    # Final score should have penalty applied
    assert scoring_result["final_score"] < 100.0
    assert len(scoring_result["penalties_applied"]) >= 1


def test_apply_scoring_logic_hook_indeterminate_matrices() -> None:
    """Test that apply_scoring_logic_hook gracefully handles indeterminate matrix evaluations."""
    state = HookState(
        execution_id="exec_0000000000000004",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "matrix_1": {"justification": "[INDETERMINATE] Missing source data"},
                "steps": [],
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    result = apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    scoring_result = delta["scoring_result"]
    assert scoring_result["total_score"] is None
    assert scoring_result["final_score"] is None
    assert "INDETERMINATE" in scoring_result["aggregation_status"]


def test_apply_scoring_logic_hook_missing_evaluative_matrices_raises() -> None:
    """Test that missing evaluative matrices without indeterminate reason raises AppException."""
    state = HookState(
        execution_id="exec_0000000000000005",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"steps": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        apply_scoring_logic_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "_evaluative_matrices' missing" in exc_info.value.message


def test_apply_scoring_logic_hook_missing_state_raises() -> None:
    """Test that apply_scoring_logic_hook raises VALIDATION_FAILED when state is None."""
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        apply_scoring_logic_hook(cast(Any, None), deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


def test_apply_scoring_logic_hook_missing_steps_in_snapshot_raises() -> None:
    """Test that apply_scoring_logic_hook raises VALIDATION_FAILED when steps key is missing."""
    state = HookState(
        execution_id="exec_0000000000000006",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"missing_steps": []}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        apply_scoring_logic_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Execution snapshot 'steps' missing" in exc_info.value.message


def test_apply_scoring_logic_hook_invalid_step_payload_raises() -> None:
    """Test that apply_scoring_logic_hook raises VALIDATION_FAILED when step payload is an invalid dict."""
    state = HookState(
        execution_id="exec_0000000000000007",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "steps": [
                    {
                        "step_id": "st_1",
                        "block_id": "blk_1",
                        "data_type": "text",
                        "payload": {"step_falsifier": "invalid_not_a_model"},
                    }
                ]
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    with pytest.raises(AppException) as exc_info:
        apply_scoring_logic_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Invalid StepOutputDTO payload" in exc_info.value.message


def test_apply_scoring_logic_hook_with_sanitization_and_panel_dto() -> None:
    """Test that apply_scoring_logic_hook extracts threat and falsifier data from SanitizationResult and StepPanelDTO."""
    sanitization_dto = SanitizationResultDTO(
        sanitized_inputs={"user_input": "Cleaned user input"},
        security_status="PASS",
        threat_detected=True,
    )
    falsifier_dto = FalsifierData(
        stress_test_findings=[
            WaltonStressTest(
                question="Is there reasoning bias?",
                evidence_held=False,
                observation="Post-hoc reasoning observed",
            )
        ],
        fidelity_audit=ReasoningFidelity(
            fidelity_score=FidelityLevel.WEAK,
            fidelity_numeric=1.0,
            abductive_score=1.0,
            plausibility_score=1.0,
            justification="Post-hoc reasoning detected",
            post_hoc_rationalization=True,
        ),
    )
    step_panel_dto = StepPanelDTO(
        falsifier_data=falsifier_dto,
    )
    state = HookState(
        execution_id="exec_0000000000000008",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "steps": [
                    {
                        "step_id": "st_primitive",
                        "block_id": "blk_prim",
                        "data_type": "text",
                        "payload": "primitive_string_payload",
                    },
                    {
                        "step_id": "st_sanit",
                        "block_id": "blk_sanit",
                        "data_type": "text",
                        "payload": {"sanitization_result": sanitization_dto.model_dump(mode="json")},
                    },
                    {
                        "step_id": "st_panel",
                        "block_id": "blk_panel",
                        "data_type": "text",
                        "payload": {"step_panel": step_panel_dto.model_dump(mode="json")},
                    },
                ],
                "inputs": {
                    "_evaluative_matrices": {"blk_1": 90.0},
                    "extra_primitive_key": "skipped_string",
                },
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )

    result = apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "scoring_result" in delta


# ==============================================================================
# 4. enforce_passivity_penalty_hook tests
# ==============================================================================


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_penalty_triggered() -> None:
    """Test that enforce_passivity_penalty_hook applies passivity penalty when raw_score <= math_min."""
    matrix_output = LightweightMatrixOutput(
        raw_score=1.0,
        normalized_score=0.0,
        justification="Base evaluation",
        evaluated_atoms={},
        extensions={},
    )

    state = HookState(
        execution_id="exec_0000000000000010",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"pb_1234567890123456": matrix_output.model_dump(mode="json")}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "pb_1234567890123456" in delta
    updated_matrix = delta["pb_1234567890123456"]
    assert "PASSIVITY PENALTY" in updated_matrix["justification"]


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_no_penalty_when_above_min() -> None:
    """Test that enforce_passivity_penalty_hook does not penalize scores above math_min."""
    matrix_output = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        justification="Strong performance",
        evaluated_atoms={},
        extensions={},
    )

    state = HookState(
        execution_id="exec_0000000000000011",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"pb_1234567890123456": matrix_output.model_dump(mode="json")}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta == {}


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_legacy_score_card_raises() -> None:
    """Test that enforce_passivity_penalty_hook fails fast if legacy score_card is present."""
    state = HookState(
        execution_id="exec_0000000000000012",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"score_card": {"dimension_1": 1.0}}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Legacy 'score_card' found" in exc_info.value.message


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_missing_workflow_repo_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises HOOK_EXECUTION_FAILED if workflow_repo is None."""
    state = HookState(
        execution_id="exec_0000000000000013",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, None),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)

    assert exc_info.value.error_code == "HOOK_EXECUTION_FAILED"


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_step_not_found_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises RESOURCE_NOT_FOUND if step is not in database."""
    mock_workflow = AsyncMock()
    mock_workflow.get_step_by_id.return_value = None
    state = HookState(
        execution_id="exec_0000000000000014",
        workflow_id="wf_1",
        step_id="st_nonexistent",
        task_blueprint="st_nonexistent",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)

    assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_matrix_has_no_scales_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED if MatrixPromptBlock has empty scales."""
    mock_workflow = AsyncMock()
    no_scales_matrix = _build_valid_pb_dict("pb_1234567890123456", scales=[])
    mock_workflow.get_step_by_id.return_value = _build_valid_step_dict(["pb_1234567890123456"])
    mock_workflow.get_prompt_block_by_id.return_value = no_scales_matrix

    state = HookState(
        execution_id="exec_0000000000000015",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_invalid_matrix_format_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED when matrix format is corrupted."""
    mock_workflow = MockRepoWaterfall()
    state = HookState(
        execution_id="exec_0000000000000016",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": {"raw_score": "not_a_number", "normalized_score": 10.0, "justification": "J"}
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Invalid LightweightMatrixOutput format" in exc_info.value.message


@pytest.mark.asyncio
async def test_enforce_passivity_penalty_hook_with_eval_map_and_bounds() -> None:
    """Test passivity penalty calculation with _evaluative_matrices dictionary update."""
    mock_workflow = MockRepoWaterfall()
    matrix_raw = {
        "raw_score": 1.0,
        "normalized_score": 20.0,
        "justification": "Low score",
        "evaluated_atoms": {},
        "extensions": {},
    }
    state = HookState(
        execution_id="exec_0000000000000017",
        workflow_id="wf_1",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "pb_1234567890123456": matrix_raw,
                "_evaluative_matrices": {"pb_1234567890123456": 20.0},
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    res = await enforce_passivity_penalty_hook(state, deps)
    assert res.success is True
    assert res.state_delta is not None
    assert "pb_1234567890123456" in res.state_delta.delta


@pytest.mark.asyncio
async def test_matrix_scoring_hook_direct_output_profile_id_resolution() -> None:
    """SSOT Invariant: matrix_scoring_hook directly accesses non-nullable output_profile_id."""
    mock_workflow = MockRepository()
    mock_workflow.get_prompt_block_by_id = AsyncMock(  # type: ignore[method-assign]
        return_value=_build_valid_pb_dict("pb_1234567890123456", [_build_valid_scale(1.0), _build_valid_scale(5.0)])
    )
    mock_workflow.get_execution = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "id": "exe_1234567890123456",
            "workflow_id": "wf_123",
            "organization_id": "org_123",
            "created_by": "usr_123",
            "active_profile_id": "prof_1111111111111111",
            "output_profile_id": "prof_1111111111111111",
            "status": "RUNNING",
            "target_locale": "fi",
            "metadata": {},
            "raw_inputs": {},
            "execution_trace": [],
            "step_states": {},
            "frozen_context": {},
        }
    )
    mock_workflow.get_output_profile_by_id = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "id": "prof_1111111111111111",
            "slug": "prof_1111111111111111",
            "name": {"translations": {"en": "Prof", "fi": "Prof"}},
            "workflow_id": "wf_123",
            "strictness_level": 85,
            "scoring_strategy": "AVERAGE",
            "target_block_order": [],
            "visible_block_extensions": [],
        }
    )

    state = HookState(
        execution_id="exe_1234567890123456",
        workflow_id="wf_123",
        step_id="st_1234567890123456",
        task_blueprint="st_1234567890123456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "results": [],
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, mock_workflow),
        workflow_repo=cast(Any, mock_workflow),
        comp_repo=cast(Any, mock_workflow),
        prompt_block_repo=cast(Any, mock_workflow),
        output_profile_repo=cast(Any, mock_workflow),
        identity_repo=cast(Any, mock_workflow),
        audit_repo=cast(Any, mock_workflow),
        system_repo=cast(Any, mock_workflow),
    )

    result = await matrix_scoring_hook(state, deps)
    assert result.success is True

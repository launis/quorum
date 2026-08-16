"""Unit tests for synthesis distiller hook wiring and context preservation.

Tests that synthesis_distiller_hook passes complete, unfiltered cognitive execution
state to both <source> block distillation and MatrixExplanationService, validates
target_locale fail-fast boundaries, handles DTO hydration, and strictly enforces
Zero Backwards Compatibility by purging legacy keys.

Phase 2, Step 3: Synthesis Distiller Wiring Unit Tests (EPIC 143).
"""

from collections.abc import Awaitable
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook


class StepOutputDTOFactory(ModelFactory[StepOutputDTO]):
    """Polyfactory factory for StepOutputDTO."""

    __model__ = StepOutputDTO


def _build_mock_deps() -> HookDependencies:
    """Helper to create fully mocked HookDependencies with standard returns matching strict Pydantic schemas."""
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    cast(AsyncMock, deps.workflow_repo.get_workflow_by_id).return_value = {
        "id": "wor_0123456789abcdef01",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Description"}},
        "status": "active",
        "version": 1,
        "organization_id": "org_0123456789abcdef01",
        "default_profile_id": "pro_0123456789abcdef01",
        "steps": [],
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    cast(AsyncMock, deps.exec_repo.get_execution).return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wor_0123456789abcdef01",
        "status": "PASSED",
        "output_profile_id": "pro_0123456789abcdef01",
        "raw_inputs": {"dynamic_inputs": {}},
        "step_states": {},
    }
    cast(AsyncMock, deps.output_profile_repo.get_output_profile_by_id).return_value = {
        "id": "pro_0123456789abcdef01",
        "slug": "prof_standard",
        "workflow_id": "wor_0123456789abcdef01",
        "name": {"default_locale": "en", "translations": {"en": "Standard Profile"}},
        "layouts": [{"preset_view": "default", "target_blocks": ["*"]}],
        "max_extension_items": 5,
    }
    cast(AsyncMock, deps.workflow_repo.get_all_steps).return_value = []
    cast(AsyncMock, deps.prompt_block_repo.get_all_prompt_blocks).return_value = []
    return deps


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_passes_unfiltered_dtos() -> None:
    """Contract: Verify unfiltered DTOs are passed to <source> blocks and assemble_matrices_to_explain."""
    deps = _build_mock_deps()

    # Step 1: Cognitive sensor finding step
    step1 = StepOutputDTO(
        step_id="stp_sensor_1",
        block_id="blk_sensor_1",
        data_type="text",
        payload={
            "findings": ["Leadership resilience verified in stress interview."],
            "evidence_quotes": [{"quote": "Leader maintained composure under pressure.", "is_verified": True}],
        },
    )
    # Step 2: Cognitive sensor finding step
    step2 = StepOutputDTO(
        step_id="stp_sensor_2",
        block_id="blk_sensor_2",
        data_type="text",
        payload={
            "findings": ["Strategic alignment demonstrated across portfolio."],
            "evidence_quotes": [{"quote": "Portfolio roadmap aligned with 2026 goals.", "is_verified": True}],
        },
    )
    # Step 3: Matrix step
    matrix_output = LightweightMatrixOutput(
        evaluated_atoms={
            "tda_0123456789abcdef01": ExecutionStatus.PASSED,
        },
        extensions={},
    )
    step3 = StepOutputDTO(
        step_id="stp_matrix_1",
        block_id="blk_matrix_1",
        data_type="matrix",
        payload=matrix_output.model_dump(mode="json"),
    )

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en", "organization_id": "org_0123456789abcdef01"},
        inputs={"steps": [step1, step2, step3]},
        global_context_vars={"organization_id": "org_0123456789abcdef01"},
    )

    with patch(
        "backend_v2.services.orchestrator.synthesis_distiller.MatrixExplanationService.assemble_matrices_to_explain"
    ) as mock_assemble:
        mock_assemble.return_value = ["matrix_explanation_1"]

        result = await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

        assert result.success is True
        assert result.state_delta is not None

        # Verify all 3 steps exist in <source> blocks inside distilled_inputs
        distilled = result.state_delta["distilled_inputs"]
        assert "Leadership resilience verified" in distilled
        assert "Strategic alignment demonstrated" in distilled
        assert "tda_0123456789abcdef01" in distilled

        # Verify MatrixExplanationService received all 3 unfiltered DTOs
        mock_assemble.assert_called_once()
        passed_dtos, passed_title_map, passed_blocks = mock_assemble.call_args[0]
        assert len(passed_dtos) == 3
        assert mock_assemble.call_args[1]["target_locale"] == "en"


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_none_state_raises_validation_failed() -> None:
    """Contract: Verify HookState is None raises AppException(VALIDATION_FAILED)."""
    deps = _build_mock_deps()

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(None, deps))  # type: ignore[arg-type]

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_invalid_inputs_type_raises_invalid_schema() -> None:
    """Contract: Verify inputs not being a dict raises AppException(INVALID_OUTPUT_SCHEMA)."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en"},
        inputs={},
        global_context_vars={},
    )
    object.__setattr__(state, "inputs", "invalid_inputs_string")

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "INVALID_OUTPUT_SCHEMA"
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_missing_steps_key_raises_validation_failed() -> None:
    """Contract: Verify missing 'steps' key in inputs raises AppException(VALIDATION_FAILED)."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en"},
        inputs={"other_key": "data"},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_missing_target_locale_raises_app_exception() -> None:
    """Contract: Verify missing 'target_locale' in metadata raises AppException(VALIDATION_FAILED)."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"organization_id": "org_0123456789abcdef01"},  # missing target_locale
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_whitespace_target_locale_raises_app_exception() -> None:
    """Contract: Verify whitespace-only 'target_locale' in metadata raises AppException(VALIDATION_FAILED)."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "   "},
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_empty_target_locale_raises_app_exception() -> None:
    """Contract: Verify empty string 'target_locale' in metadata raises AppException(VALIDATION_FAILED)."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": ""},
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_dict_steps_hydrated_successfully() -> None:
    """Contract: Verify raw dictionary items in inputs['steps'] are hydrated via StepOutputDTO."""
    deps = _build_mock_deps()

    raw_step_dict: dict[str, Any] = {
        "step_id": "stp_raw_dict_1",
        "block_id": "blk_raw_dict_1",
        "data_type": "text",
        "payload": {
            "summary": "Raw dict step parsed successfully.",
        },
    }

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en", "organization_id": "org_0123456789abcdef01"},
        inputs={"steps": [raw_step_dict]},
        global_context_vars={"organization_id": "org_0123456789abcdef01"},
    )

    result = await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "Raw dict step parsed successfully" in result.state_delta["distilled_inputs"]


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_missing_output_profile_id_raises_config_error() -> None:
    """Contract: Verify missing output_profile_id on execution record raises AppException(CONFIGURATION_ERROR)."""
    deps = _build_mock_deps()
    cast(AsyncMock, deps.exec_repo.get_execution).return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wor_0123456789abcdef01",
        "status": "PASSED",
        "output_profile_id": None,  # Missing profile ID
        "raw_inputs": {"dynamic_inputs": {}},
        "step_states": {},
    }

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en"},
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "CONFIGURATION_ERROR"
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_workflow_not_found_raises_resource_not_found() -> None:
    """Contract: Verify workflow not found in repo raises AppException(RESOURCE_NOT_FOUND)."""
    deps = _build_mock_deps()
    cast(AsyncMock, deps.workflow_repo.get_workflow_by_id).return_value = None

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_missing_0123456789",
        metadata={"target_locale": "en"},
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_output_profile_not_found_raises_resource_not_found() -> None:
    """Contract: Verify output profile not found in repo raises AppException(RESOURCE_NOT_FOUND)."""
    deps = _build_mock_deps()
    cast(AsyncMock, deps.output_profile_repo.get_output_profile_by_id).return_value = None

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en"},
        inputs={"steps": []},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "RESOURCE_NOT_FOUND"
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_state_delta_purges_legacy_language_key() -> None:
    """Contract: Verify state_delta contains 'target_locale' and STRICTLY DOES NOT contain 'language'."""
    deps = _build_mock_deps()

    step_output = StepOutputDTO(
        step_id="stp_clean_1",
        block_id="blk_clean_1",
        data_type="text",
        payload={"data": "test clean delta"},
    )

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "FI", "organization_id": "org_0123456789abcdef01"},
        inputs={"steps": [step_output]},
        global_context_vars={"organization_id": "org_0123456789abcdef01"},
    )

    result = await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None

    # Zero Backwards Compatibility validation (the_no_legacy_mandate)
    assert "target_locale" in result.state_delta
    assert result.state_delta["target_locale"] == "fi"
    assert "language" not in result.state_delta


@pytest.mark.asyncio
async def test_synthesis_distiller_wiring_string_payload_fails_fast() -> None:
    """Contract: Verify non-dict/non-list payload in StepOutputDTO fails fast during compression in distillation."""
    deps = _build_mock_deps()

    step_output = StepOutputDTO(
        step_id="stp_string_payload_1",
        block_id="blk_string_payload_1",
        data_type="text",
        payload="plain string scalar payload",
    )

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata={"target_locale": "en", "organization_id": "org_0123456789abcdef01"},
        inputs={"steps": [step_output]},
        global_context_vars={"organization_id": "org_0123456789abcdef01"},
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 400
    assert "Payload must be a dict or list for compression" in exc_info.value.message

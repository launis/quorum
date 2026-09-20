"""Unit tests for the Synthesis Distiller Hook.

Epic 93 Phase 2, Milestone 1.7: Tests for metadata stripping and matrices_to_explain assembly.
"""

import json
from typing import Any
from unittest.mock import patch

import pytest

from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor
from backend_v2.settings import Settings


def test_compress_synthesis_payload_strips_heavy_keys() -> None:
    """Test that _compress_synthesis_payload removes log-heavy keys but preserves lite evaluations."""
    payload: dict[str, Any] = {
        "normalized_score": 75.0,
        "level_breakdown": {"1": 2, "3": 1},
        "shuffled_atoms": ["atom1", "atom2", "atom3"],
        "results": [
            {
                "atom_id": "a1",
                "exact_quotes": ["This is a valid quote."],
                "semantic_reasoning": "Strong reasoning trace.",
                "some_extra": "data",
            },
            {
                "atom_id": "a2",
                "exact_quotes": ["None"],
                "semantic_reasoning": "Weak reasoning.",
            },
        ],
    }
    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert "shuffled_atoms" not in compressed_str
    assert "This is a valid quote." in compressed_str
    # "None" is filtered out as invalid
    assert '"atom_id": "a2"' not in compressed_str


def test_compress_synthesis_payload_caps_evaluations_at_40() -> None:
    """PROMISE: Prevent LLM token explosion by stratifying and capping evaluations at settings.max_synthesis_evaluations."""
    evals = [
        {
            "atom_id": f"a{i}",
            "exact_quotes": [f"Quote {i}"],
            "semantic_reasoning": f"Reason {i}",
        }
        for i in range(50)
    ]
    payload: dict[str, Any] = {"results": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=40),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    pruned = compressed_dict.get("results", [])
    assert len(pruned) == 40


def test_compress_synthesis_payload_handles_string_input() -> None:
    """PROMISE: Test that _compress_synthesis_payload strips whitespace for plain string values and fails fast on empty."""
    import pytest

    from backend_v2.exceptions import AppException

    # Valid string returns trimmed string
    res = SynthesisPayloadCompressor.compress_synthesis_payload("  plain text value  ")
    assert res == "plain text value"

    # Empty or whitespace string fails fast
    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload("   ")
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_synthesis_payload_strips_null_quotes() -> None:
    """PROMISE: Verify that _compress_synthesis_payload fails fast if all quotes are stripped."""
    payload: dict[str, Any] = {
        "results": [
            {
                "atom_id": "a1",
                "exact_quotes": [
                    "N/A",
                    "null",
                    "N/A - insufficient data",
                    "[INDETERMINATE]",
                ],
                "semantic_reasoning": "Test",
            },
        ],
    }
    import pytest

    from backend_v2.exceptions import AppException

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_compress_synthesis_payload_compresses_anchors() -> None:
    """Verify that _compress_synthesis_payload handles nested structures recursively."""
    payload: dict[str, Any] = {
        "localized_anchors_found": {"doc1": True, "doc2": False},
        "post_quote_anchor": "should remain",
        "nested": {
            "shuffled_atoms": ["should", "be", "stripped"],
            "value": 42,
        },
    }
    compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
    assert "shuffled_atoms" not in compressed_str
    assert "value" in compressed_str
    assert "localized_anchors_found" in compressed_str


def test_build_title_map_with_blocks_and_steps() -> None:
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.prompt_blocks import PromptBlock, SystemRulePromptBlock
    from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
    from backend_v2.models.domain.workflow import Workflow
    from backend_v2.models.enums import (
        BlockDataType,
        CognitiveTier,
        HistoricalContextMode,
        PromptBlockCategory,
        StepType,
    )
    from backend_v2.services.orchestrator.synthesis_distiller import _build_title_map

    blocks_by_id: dict[str, PromptBlock] = {
        "blk_1234567890abcdef": SystemRulePromptBlock(
            id="blk_1234567890abcdef",
            slug="test_block",
            type=BlockDataType.INSTRUCTION,
            category_id=PromptBlockCategory.SYSTEM_RULE,
            label=I18nText(translations={"en": "Block Label EN", "fi": "Lohkon nimi FI"}),
            description=I18nText(translations={"en": "Desc"}),
        )
    }

    step_blueprint = Step(
        id="sp_1111111111111111",
        slug="step_one",
        name=I18nText(translations={"en": "Step Blueprint Name"}),
        cognitive_tier=CognitiveTier.FAST,
        type=StepType.LOGIC,
        hook="text_consolidation_hook",
    )

    wf = Workflow(
        id="wf_1111111111111111",
        slug="test_wf",
        name=I18nText(translations={"en": "Workflow Name"}),
        description=I18nText(translations={"en": "Workflow Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1111111111111111",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="cfg_model_registry_01",
        steps=[StepRule(id="sr_1111111111111111", task_blueprint="sp_1111111111111111")],
        expected_inputs=[
            ExpectedInput(
                input_key="interview_text",
                label=I18nText(translations={"en": "Interview Text"}),
                description=I18nText(translations={"en": "Interview Text"}),
                required=True,
                input_modes=["paste"],
            )
        ],
    )

    # Resolve FI
    title_map = _build_title_map(wf, [step_blueprint], "fi", blocks_by_id)
    assert title_map["blk_1234567890abcdef"] == "Lohkon nimi FI"
    assert title_map["sr_1111111111111111"] == "Step Blueprint Name"
    assert title_map["interview_text"] == "Interview Text"

    # None workflow
    title_map_none = _build_title_map(None, [], "en", blocks_by_id)
    assert title_map_none["blk_1234567890abcdef"] == "Block Label EN"


def test_build_title_map_missing_blueprint_raises() -> None:
    import pytest

    from backend_v2.exceptions import AppException
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.domain.workflow import Workflow
    from backend_v2.models.enums import HistoricalContextMode
    from backend_v2.services.orchestrator.synthesis_distiller import _build_title_map

    wf = Workflow(
        id="wf_1111111111111111",
        slug="test_wf",
        name=I18nText(translations={"en": "Workflow Name"}),
        description=I18nText(translations={"en": "Workflow Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1111111111111111",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="cfg_model_registry_01",
        steps=[StepRule(id="sr_1111111111111111", task_blueprint="sp_2222222222222222")],
    )

    with pytest.raises(AppException) as exc_info:
        _build_title_map(wf, [], "en")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_build_historical_context_all_branches() -> None:
    from datetime import datetime, timezone
    from unittest.mock import AsyncMock

    from backend_v2.core.hook_registry import (
        ExecutionInputsDTO,
        GlobalContextVarsDTO,
        HookDependencies,
        HookState,
    )
    from backend_v2.models.domain.execution import ExecutionRecord
    from backend_v2.models.domain.synthesis import RenderedSynthesisCache
    from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.models.view.sdui import ParagraphBlock
    from backend_v2.services.orchestrator.synthesis_distiller import _fetch_historical_context

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

    state = HookState(
        execution_id="ex_0000000000000000",
        workflow_id="wf_1111111111111111",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(vars={"user_id": "u1", "organization_id": "org1"}),
        inputs=ExecutionInputsDTO(),
    )

    # 1. Disabled mode
    res = await _fetch_historical_context(HistoricalContextMode.DISABLED, deps, state, "prof_1")
    assert res == ""

    # 2. No user or org
    empty_state = HookState(
        execution_id="ex_0000000000000000",
        workflow_id="wf_1111111111111111",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(),
    )
    res = await _fetch_historical_context(HistoricalContextMode.SLIDING_WINDOW_3, deps, empty_state, "prof_1")
    assert res == ""

    # 3. Valid past executions
    past_exec1 = ExecutionRecord(
        id="ex_1111111111111111",
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1",
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        completed_at=datetime.now(timezone.utc),
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={
            "prof_1": RenderedSynthesisCache(
                section_syntheses={"sec1": [ParagraphBlock(text="Past synthesis 1", exact_quotes=[], citations=[])]},
            )
        },
    )
    past_exec2 = ExecutionRecord(
        id="ex_0000000000000000",  # should be ignored (matches state.execution_id)
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1",
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    past_exec3 = ExecutionRecord(
        id="ex_2222222222222222",  # should be ignored
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1",
        status=ExecutionStatus.FAILED,
        progress=0,
        status_message="Failed",
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    cast_repo = deps.exec_repo
    cast_repo.get_all_executions.return_value = [past_exec1, past_exec2, past_exec3]  # type: ignore[attr-defined]

    res = await _fetch_historical_context(HistoricalContextMode.SLIDING_WINDOW_3, deps, state, "prof_1")
    assert "<HistoricalContext>" in res
    assert "Past synthesis 1" in res

    # 4. Past execs with missing profile, empty sections, or empty blocks
    past_exec_wrong_profile = ExecutionRecord(
        id="ex_3333333333333333",
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_2",
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={
            "prof_2": RenderedSynthesisCache(
                section_syntheses={"sec1": [ParagraphBlock(text="Wrong prof", exact_quotes=[], citations=[])]},
            )
        },
    )
    past_exec_empty_sections = ExecutionRecord(
        id="ex_4444444444444444",
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1",
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={
            "prof_1": RenderedSynthesisCache(
                section_syntheses={},
            )
        },
    )
    past_exec_empty_blocks = ExecutionRecord(
        id="ex_5555555555555555",
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1",
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={
            "prof_1": RenderedSynthesisCache(
                section_syntheses={"sec1": []},
            )
        },
    )
    cast_repo.get_all_executions.return_value = [
        past_exec_wrong_profile,
        past_exec_empty_sections,
        past_exec_empty_blocks,
    ]
    res_empty = await _fetch_historical_context(HistoricalContextMode.SLIDING_WINDOW_3, deps, state, "prof_1")
    assert res_empty == ""


@pytest.mark.asyncio
async def test_synthesis_distiller_step_inputs_and_rules_branches() -> None:
    from typing import cast
    from unittest.mock import AsyncMock

    from backend_v2.core.hook_registry import (
        ExecutionInputsDTO,
        GlobalContextVarsDTO,
        HookState,
    )
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import Step
    from backend_v2.models.enums import CognitiveTier, StepType
    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.models.state import StepOutputDTO
    from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook
    from backend_v2.tests.unit.services.orchestrator.test_synthesis_distiller_wiring import (
        _build_mock_deps,
    )

    deps = _build_mock_deps()
    bp1 = Step(
        id="bp_0123456789abcdef01",
        slug="step_bp1",
        name=I18nText(translations={"en": "Blueprint 1"}),
        cognitive_tier=CognitiveTier.FAST,
        type=StepType.LOGIC,
        hook="text_consolidation_hook",
    )
    bp2 = Step(
        id="bp_0123456789abcdef02",
        slug="step_bp2",
        name=I18nText(translations={"en": "Blueprint 2"}),
        cognitive_tier=CognitiveTier.FAST,
        type=StepType.LOGIC,
        hook="text_consolidation_hook",
    )
    cast(AsyncMock, deps.workflow_repo.get_all_steps).return_value = [bp1, bp2]
    cast(AsyncMock, deps.workflow_repo.get_workflow_by_id).return_value = {
        "id": "wor_0123456789abcdef01",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test Workflow"}},
        "description": {"translations": {"en": "Test Description"}},
        "status": "active",
        "version": 1,
        "organization_id": "org_0123456789abcdef01",
        "default_profile_id": "pro_0123456789abcdef01",
        "steps": [
            {
                "id": "stp_0123456789abcdef01",
                "task_blueprint": "bp_0123456789abcdef01",
                "is_synthesis_source": True,
            },
            {
                "id": "stp_0123456789abcdef02",
                "task_blueprint": "bp_0123456789abcdef02",
                "is_synthesis_source": False,
            },
        ],
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
    }

    # Case 1: single StepOutputDTO in steps_data (line 233)
    single_step = StepOutputDTO(
        step_id="stp_0123456789abcdef01",
        block_id="blk_0123456789abcdef01",
        data_type="text",
        payload="Single step text payload",
    )
    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            dynamic_inputs={"steps": single_step},
            target_locale="en",
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"organization_id": "org_0123456789abcdef01"}),
    )
    result = await synthesis_distiller_hook(state, deps)
    assert result.success is True

    # Case 2: list with is_synthesis_source=False, block_id starting with _, and empty payload (lines 321-323, 329, 331, 337-342)
    step_false = StepOutputDTO(
        step_id="stp_0123456789abcdef02",
        block_id="blk_0123456789abcdef02",
        data_type="text",
        payload="Should be skipped as non-synthesis source",
    )
    step_internal = StepOutputDTO(
        step_id="stp_0123456789abcdef03",
        block_id="_internal_block",
        data_type="text",
        payload="Should be skipped due to underscore",
    )
    step_empty = StepOutputDTO(
        step_id="stp_0123456789abcdef04",
        block_id="blk_0123456789abcdef04",
        data_type="text",
        payload=None,
    )
    state_multi = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            dynamic_inputs={"steps": [single_step, step_false, step_internal, step_empty]},
            target_locale="en",
        ),
        global_context_vars=GlobalContextVarsDTO(vars={"organization_id": "org_0123456789abcdef01"}),
    )
    res_multi = await synthesis_distiller_hook(state_multi, deps)
    assert res_multi.success is True


# Import all wiring test functions so backend_audit_loop discovers and runs them
from backend_v2.tests.unit.services.orchestrator.test_synthesis_distiller_wiring import (
    test_synthesis_distiller_wiring_dict_steps_hydrated_successfully,
    test_synthesis_distiller_wiring_empty_target_locale_raises_app_exception,
    test_synthesis_distiller_wiring_invalid_inputs_type_raises_invalid_schema,
    test_synthesis_distiller_wiring_missing_output_profile_id_raises_config_error,
    test_synthesis_distiller_wiring_missing_steps_key_raises_validation_failed,
    test_synthesis_distiller_wiring_missing_target_locale_raises_app_exception,
    test_synthesis_distiller_wiring_none_state_raises_validation_failed,
    test_synthesis_distiller_wiring_output_profile_not_found_raises_resource_not_found,
    test_synthesis_distiller_wiring_passes_unfiltered_dtos,
    test_synthesis_distiller_wiring_state_delta_purges_legacy_language_key,
    test_synthesis_distiller_wiring_whitespace_target_locale_raises_app_exception,
    test_synthesis_distiller_wiring_workflow_not_found_raises_resource_not_found,
)

__all__ = [
    "test_compress_synthesis_payload_caps_evaluations_at_40",
    "test_compress_synthesis_payload_compresses_anchors",
    "test_compress_synthesis_payload_handles_string_input",
    "test_compress_synthesis_payload_strips_heavy_keys",
    "test_compress_synthesis_payload_strips_null_quotes",
    "test_synthesis_distiller_wiring_dict_steps_hydrated_successfully",
    "test_synthesis_distiller_wiring_empty_target_locale_raises_app_exception",
    "test_synthesis_distiller_wiring_invalid_inputs_type_raises_invalid_schema",
    "test_synthesis_distiller_wiring_missing_output_profile_id_raises_config_error",
    "test_synthesis_distiller_wiring_missing_steps_key_raises_validation_failed",
    "test_synthesis_distiller_wiring_missing_target_locale_raises_app_exception",
    "test_synthesis_distiller_wiring_none_state_raises_validation_failed",
    "test_synthesis_distiller_wiring_output_profile_not_found_raises_resource_not_found",
    "test_synthesis_distiller_wiring_passes_unfiltered_dtos",
    "test_synthesis_distiller_wiring_state_delta_purges_legacy_language_key",
    "test_synthesis_distiller_wiring_whitespace_target_locale_raises_app_exception",
    "test_synthesis_distiller_wiring_workflow_not_found_raises_resource_not_found",
]

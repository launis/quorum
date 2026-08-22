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
        "evaluations": [
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
    payload: dict[str, Any] = {"evaluations": evals}

    with patch(
        "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
        return_value=Settings(max_synthesis_evaluations=40),
    ):
        compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        compressed_dict = json.loads(compressed_str)

    pruned = compressed_dict.get("evaluations", [])
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
        "evaluations": [
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
    from backend_v2.models.enums import HistoricalContextMode
    from backend_v2.models.v2_core import ExpectedInput, I18nText, PromptBlock, Step, StepRule, Workflow
    from backend_v2.services.orchestrator.synthesis_distiller import _build_title_map

    blocks_by_id = {
        "blk_1234567890abcdef": PromptBlock(
            id="blk_1234567890abcdef",
            slug="test_block",
            type="instruction",
            category_id="system_rule",
            label=I18nText(default_locale="en", translations={"en": "Block Label EN", "fi": "Lohkon nimi FI"}),
            description=I18nText(default_locale="en", translations={"en": "Desc"}),
        )
    }

    step_blueprint = Step(
        id="sp_1111111111111111",
        slug="step_one",
        name=I18nText(default_locale="en", translations={"en": "Step Blueprint Name"}),
        model_strategy="fast",
        type="logic",
        hook="text_consolidation_hook",
    )

    wf = Workflow(
        id="wf_1111111111111111",
        slug="test_wf",
        name=I18nText(default_locale="en", translations={"en": "Workflow Name"}),
        description=I18nText(default_locale="en", translations={"en": "Workflow Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1111111111111111",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[StepRule(id="sr_1111111111111111", task_blueprint="sp_1111111111111111")],
        expected_inputs=[
            ExpectedInput(
                input_key="interview_text",
                label=I18nText(default_locale="en", translations={"en": "Interview Text"}),
                description=I18nText(default_locale="en", translations={"en": "Interview Text"}),
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
    from backend_v2.models.enums import HistoricalContextMode
    from backend_v2.models.v2_core import I18nText, StepRule, Workflow
    from backend_v2.services.orchestrator.synthesis_distiller import _build_title_map

    wf = Workflow(
        id="wf_1111111111111111",
        slug="test_wf",
        name=I18nText(default_locale="en", translations={"en": "Workflow Name"}),
        description=I18nText(default_locale="en", translations={"en": "Workflow Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1111111111111111",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[StepRule(id="sr_1111111111111111", task_blueprint="sp_2222222222222222")],
    )

    with pytest.raises(AppException) as exc_info:
        _build_title_map(wf, [], "en")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_build_historical_context_all_branches() -> None:
    from datetime import datetime, timezone
    from unittest.mock import AsyncMock

    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
    from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache
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
        metadata={"target_locale": "en"},
        global_context_vars={"user_id": "u1", "organization_id": "org1"},
        inputs={},
    )

    # 1. Disabled mode
    res = await _fetch_historical_context(HistoricalContextMode.DISABLED, deps, state, "prof_1")
    assert res == ""

    # 2. No user or org
    empty_state = HookState(
        execution_id="ex_0000000000000000",
        workflow_id="wf_1111111111111111",
        metadata={"target_locale": "en"},
        global_context_vars={},
        inputs={},
    )
    res = await _fetch_historical_context(HistoricalContextMode.SLIDING_WINDOW_3, deps, empty_state, "prof_1")
    assert res == ""

    # 3. Valid past executions
    past_exec1 = ExecutionRecord(
        id="ex_1111111111111111",
        workflow_id="wf_1111111111111111",
        status=ExecutionStatus.PASSED,
        completed_at=datetime.now(timezone.utc),
        profile_syntheses={
            "prof_1": RenderedSynthesisCache(
                section_syntheses={"sec1": [ParagraphBlock(text="Past synthesis 1")]},
            )
        },
    )
    past_exec2 = ExecutionRecord(
        id="ex_0000000000000000",  # should be ignored (matches state.execution_id)
        workflow_id="wf_1111111111111111",
        status=ExecutionStatus.PASSED,
    )
    past_exec3 = ExecutionRecord(
        id="ex_2222222222222222",  # should be ignored
        workflow_id="wf_1111111111111111",
        status=ExecutionStatus.FAILED,
    )

    cast_repo = deps.exec_repo
    cast_repo.get_all_executions.return_value = [past_exec1, past_exec2, past_exec3]  # type: ignore[attr-defined]

    res = await _fetch_historical_context(HistoricalContextMode.SLIDING_WINDOW_3, deps, state, "prof_1")
    assert "<HistoricalContext>" in res
    assert "Past synthesis 1" in res


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

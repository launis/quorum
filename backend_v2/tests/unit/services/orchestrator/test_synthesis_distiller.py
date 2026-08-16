"""Unit tests for the Synthesis Distiller Hook.

Epic 93 Phase 2, Milestone 1.7: Tests for metadata stripping and matrices_to_explain assembly.
"""

from typing import Any

from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor


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
    """PROMISE: Prevent LLM token explosion by failing fast on excessive evaluations."""
    evals = [
        {
            "atom_id": f"a{i}",
            "exact_quotes": [f"Quote {i}"],
            "semantic_reasoning": f"Reason {i}",
        }
        for i in range(50)
    ]
    payload: dict[str, Any] = {"evaluations": evals}

    import pytest

    from backend_v2.exceptions import AppException

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload(payload)

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


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

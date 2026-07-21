from unittest.mock import AsyncMock
"""Unit tests for the Synthesis Distiller Hook.

Epic 93 Phase 2, Milestone 1.7: Tests for metadata stripping and matrices_to_explain assembly.
"""

from typing import Any

from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.synthesis_distiller import (
    _assemble_matrices_to_explain,
    _compress_synthesis_payload,
)


def test_compress_synthesis_payload_strips_heavy_keys() -> None:
    """Test that _compress_synthesis_payload removes log-heavy keys but preserves lite evaluations."""
    payload: dict[str, Any] = {
        "normalized_score": 75.0,
        "level_breakdown": {"1": 2, "3": 1},
        "shuffled_atoms": ["atom1", "atom2", "atom3"],
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quotes": [{"quote": "This is a valid quote."}],
                "semantic_reasoning": "Strong reasoning trace.",
                "some_extra": "data",
            },
            {
                "atom_id": "a2",
                "exact_quotes": [{"quote": "None"}],
                "semantic_reasoning": "Weak reasoning.",
            },
        ],
    }
    compressed_str = _compress_synthesis_payload(payload)

    assert "shuffled_atoms" not in compressed_str
    assert "This is a valid quote." in compressed_str
    # "None" is filtered out as invalid
    assert '"atom_id": "a2"' not in compressed_str


def test_compress_synthesis_payload_caps_evaluations_at_20() -> None:
    """Test that _compress_synthesis_payload caps evaluations at 20 items."""
    evals = [
        {
            "atom_id": f"a{i}",
            "exact_quotes": [{"quote": f"Quote {i}"}],
            "semantic_reasoning": f"Reason {i}",
        }
        for i in range(30)
    ]
    payload: dict[str, Any] = {"evaluations": evals}

    compressed_str = _compress_synthesis_payload(payload)

    import json

    parsed = json.loads(compressed_str)
    assert len(parsed["evaluations"]) == 20


def test_compress_synthesis_payload_handles_string_input() -> None:
    """Test that _compress_synthesis_payload handles plain string values."""
    result = _compress_synthesis_payload("plain text value")
    assert result == "plain text value"


def test_compress_synthesis_payload_strips_null_quotes() -> None:
    """Verify that _compress_synthesis_payload strips invalid null-like quote values."""
    payload: dict[str, Any] = {
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quotes": [
                    {"quote": "N/A"},
                    {"quote": "null"},
                    {"quote": "N/A - insufficient data"},
                    {"quote": "[INDETERMINATE]"},
                ],
                "semantic_reasoning": "Test",
            },
        ],
    }
    compressed_str = _compress_synthesis_payload(payload)
    # All quotes are filtered as invalid, so evaluation entry is dropped
    assert "evaluations" not in compressed_str


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
    compressed_str = _compress_synthesis_payload(payload)
    assert "shuffled_atoms" not in compressed_str
    assert "value" in compressed_str
    assert "localized_anchors_found" in compressed_str


def test_assemble_matrices_to_explain_basic() -> None:
    """Test basic assembly of matrices_to_explain from scored payloads with evaluated_atoms."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "level_breakdown": {"3": 2},
                "evaluated_atoms": [
                    {"atom_id": "a1", "exact_quotes": [{"quote": "Quote A from source."}]},
                    {"atom_id": "a2", "exact_quotes": [{"quote": "Quote B from source."}]},
                ],
            },
        ),
    ]
    result = _assemble_matrices_to_explain(dtos)

    assert len(result) == 1
    assert result[0]["matrix_id"] == "MX-0"
    assert result[0]["real_matrix_id"] == "blk_matrix1"
    assert result[0]["score"] == 78.5
    assert "Quote A from source." in result[0]["justification"]
    assert "Quote B from source." in result[0]["justification"]


def test_assemble_matrices_to_explain_no_matching_quotes() -> None:
    """Test that matrices without evaluated_atoms are excluded."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={"normalized_score": 78.5},
        ),
    ]
    result = _assemble_matrices_to_explain(dtos)
    assert len(result) == 0


def test_assemble_matrices_to_explain_empty_quotes_list() -> None:
    """Test that matrices with empty quote lists are excluded."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={"normalized_score": 78.5, "evaluated_atoms": [{"atom_id": "a1", "exact_quotes": []}]},
        ),
    ]
    result = _assemble_matrices_to_explain(dtos)
    assert len(result) == 0


def test_assemble_matrices_to_explain_deduplicates_by_block_id() -> None:
    """Test that duplicate block_id entries are deduplicated (first wins)."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_m1",
            data_type="matrix",
            payload={
                "normalized_score": 50.0,
                "evaluated_atoms": [{"atom_id": "a1", "exact_quotes": [{"quote": "Quote 1"}]}],
            },
        ),
        StepOutputDTO(
            step_id="step2",
            block_id="blk_m1",
            data_type="matrix",
            payload={
                "normalized_score": 90.0,
                "evaluated_atoms": [{"atom_id": "a1", "exact_quotes": [{"quote": "Quote 2"}]}],
            },
        ),
    ]
    result = _assemble_matrices_to_explain(dtos)
    assert len(result) == 1
    assert result[0]["score"] == 50.0  # First entry wins

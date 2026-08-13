"""Unit tests for the Matrix Explanation Service.

Epic 142 Phase 3: Tests for matrix explanation context generation.
"""

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.matrix_explanation_service import MatrixExplanationService


def test_assemble_matrices_to_explain_basic() -> None:
    """Test basic assembly of matrices_to_explain from scored payloads with evaluated_atoms."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [
                    {"tda_id": "a1", "exact_quotes": ["Quote A from source."]},
                    {"tda_id": "a2", "exact_quotes": ["Quote B from source."]},
                ],
                "evaluated_atoms": {
                    "a1": ExecutionStatus.PASSED.value,
                    "a2": ExecutionStatus.PASSED.value,
                },
            },
        ),
    ]

    from typing import cast
    from unittest.mock import MagicMock

    mock_pb_magic = MagicMock(spec=PromptBlock)
    mock_pb_magic.category_id = "matrix"
    mock_pb_magic.scales = None
    mock_pb = cast(PromptBlock, mock_pb_magic)
    blocks_by_id = {"blk_matrix1": mock_pb}

    result = MatrixExplanationService.assemble_matrices_to_explain(dtos, title_map={}, blocks_by_id=blocks_by_id)

    assert len(result) == 1
    assert result[0].matrix_id == "MX-0"
    assert result[0].real_matrix_id == "blk_matrix1"
    assert result[0].score == 78.5
    assert "Quote A from source." in result[0].justification
    assert "Quote B from source." in result[0].justification


def test_assemble_matrices_to_explain_no_matching_quotes() -> None:
    """Test that matrices without evaluated_atoms are INCLUDED to prevent Fail-Fast crash in blueprint.py."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={"normalized_score": 78.5},
        ),
    ]

    from typing import cast
    from unittest.mock import MagicMock

    mock_pb_magic = MagicMock(spec=PromptBlock)
    mock_pb_magic.category_id = "matrix"
    mock_pb_magic.scales = None
    mock_pb = cast(PromptBlock, mock_pb_magic)
    blocks_by_id = {"blk_matrix1": mock_pb}

    result = MatrixExplanationService.assemble_matrices_to_explain(dtos, title_map={}, blocks_by_id=blocks_by_id)
    assert len(result) == 1
    assert result[0].justification == "No direct evidence quotes extracted for this matrix."


def test_assemble_matrices_to_explain_empty_quotes_list() -> None:
    """Test that matrices with empty quote lists are INCLUDED with a fallback justification to prevent Fail-Fast crash in blueprint.py."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [{"tda_id": "a1", "exact_quotes": []}],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED.value},
            },
        ),
    ]

    from typing import cast
    from unittest.mock import MagicMock

    mock_pb_magic = MagicMock(spec=PromptBlock)
    mock_pb_magic.category_id = "matrix"
    mock_pb_magic.scales = None
    mock_pb = cast(PromptBlock, mock_pb_magic)
    blocks_by_id = {"blk_matrix1": mock_pb}

    result = MatrixExplanationService.assemble_matrices_to_explain(dtos, title_map={}, blocks_by_id=blocks_by_id)
    assert len(result) == 1
    assert result[0].real_matrix_id == "blk_matrix1"
    assert result[0].justification == "No direct evidence quotes extracted for this matrix."


def test_assemble_matrices_to_explain_deduplicates_by_block_id() -> None:
    """Test that duplicate block_id entries are deduplicated (first wins)."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_m1",
            data_type="matrix",
            payload={
                "normalized_score": 50.0,
                "results": [{"tda_id": "a1", "exact_quotes": ["Quote 1"]}],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED.value},
            },
        ),
        StepOutputDTO(
            step_id="step2",
            block_id="blk_m1",
            data_type="matrix",
            payload={
                "normalized_score": 90.0,
                "results": [{"tda_id": "a1", "exact_quotes": ["Quote 2"]}],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED.value},
            },
        ),
    ]

    from typing import cast
    from unittest.mock import MagicMock

    mock_pb_magic = MagicMock(spec=PromptBlock)
    mock_pb_magic.category_id = "matrix"
    mock_pb_magic.scales = None
    mock_pb = cast(PromptBlock, mock_pb_magic)
    blocks_by_id = {"blk_m1": mock_pb}

    result = MatrixExplanationService.assemble_matrices_to_explain(dtos, title_map={}, blocks_by_id=blocks_by_id)
    assert len(result) == 1
    assert result[0].score == 50.0  # First entry wins


def test_assemble_matrices_to_explain_includes_failed_claims() -> None:
    """PROMISE: Matrix explanation must include FAILED claims and skip N_A claims."""
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id="blk_matrix1",
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [
                    {"tda_id": "a1", "exact_quotes": ["Quote A for pass."]},
                    {"tda_id": "a2", "exact_quotes": ["Quote B for fail."]},
                    {"tda_id": "a3", "exact_quotes": ["Quote C for NA."]},
                ],
                "evaluated_atoms": {
                    "a1": ExecutionStatus.PASSED.value,
                    "a2": ExecutionStatus.FAILED.value,
                    "a3": ExecutionStatus.N_A.value,
                },
            },
        ),
    ]

    from typing import cast
    from unittest.mock import MagicMock

    mock_pb_magic = MagicMock(spec=PromptBlock)
    mock_pb_magic.category_id = "matrix"
    mock_pb_magic.scales = None
    mock_pb = cast(PromptBlock, mock_pb_magic)
    blocks_by_id = {"blk_matrix1": mock_pb}

    result = MatrixExplanationService.assemble_matrices_to_explain(dtos, title_map={}, blocks_by_id=blocks_by_id)

    assert len(result) == 1
    assert "Quote A for pass." in result[0].justification
    assert "Quote B for fail." in result[0].justification
    assert "Quote C for NA." not in result[0].justification

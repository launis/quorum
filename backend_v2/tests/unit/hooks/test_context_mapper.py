"""Unit tests for context_mapper hook module."""

from typing import Any

import pytest

from backend_v2.exceptions import AppException
from backend_v2.hooks.context_mapper import ContextMapper
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock


def test_context_mapper_build_ordinal_mapping_empty() -> None:
    """Test that empty target_blocks or wildcard returns empty string."""
    assert ContextMapper.build_ordinal_mapping([]) == ""
    assert ContextMapper.build_ordinal_mapping(["*"]) == ""


def test_context_mapper_build_ordinal_mapping_success() -> None:
    """Test successful ordinal mapping compilation with scales."""
    scales = [
        MatrixScale(score=1, ai_label="LOW", name=I18nText(translations={"en": "Low", "fi": "Matala"})),
        MatrixScale(score=5, ai_label="HIGH", name=I18nText(translations={"en": "High", "fi": "Korkea"})),
    ]
    pb_matrix = MatrixPromptBlock(
        id="pb_0123456789abcdef",
        slug="matrix_1",
        label=I18nText(translations={"en": "Matrix", "fi": "Matriisi"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        scales=scales,
    )
    pb_instruction = SystemRulePromptBlock(
        id="pb_fedcba9876543210",
        slug="inst_1",
        label=I18nText(translations={"en": "Inst", "fi": "Ohje"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
    )

    mapping = ContextMapper.build_ordinal_mapping(
        ["pb_0123456789abcdef", "pb_fedcba9876543210"], [pb_matrix, pb_instruction]
    )
    assert "TARGET DATA MAPPING" in mapping
    assert "Target Data Element -> ID: pb_0123456789abcdef (Absolute Scale Limits: 1 to 5)" in mapping
    assert "Target Data Element -> ID: pb_fedcba9876543210\n" in mapping


def test_context_mapper_build_ordinal_mapping_invalid_block_type_raises() -> None:
    """Test that non-PromptBlockBase dict in all_blocks raises DATA_CORRUPTION AppException."""
    invalid_blocks: Any = [{"id": "pb_1"}]
    with pytest.raises(AppException) as exc_info:
        ContextMapper.build_ordinal_mapping(["pb_1"], invalid_blocks)

    assert exc_info.value.error_code == "DATA_CORRUPTION"
    assert exc_info.value.status_code == 500


def test_context_mapper_build_ordinal_mapping_mixed_invalid_element_raises() -> None:
    """Test that a corrupted non-model element after a valid block in all_blocks raises AppException."""
    valid_block = SystemRulePromptBlock(
        id="pb_fedcba9876543210",
        slug="inst_1",
        label=I18nText(translations={"en": "Inst", "fi": "Ohje"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
    )
    mixed_blocks: Any = [valid_block, "corrupted_raw_string"]
    with pytest.raises(AppException) as exc_info:
        ContextMapper.build_ordinal_mapping(["pb_0123456789abcdef"], mixed_blocks)

    assert exc_info.value.error_code == "DATA_CORRUPTION"
    assert exc_info.value.status_code == 500


def test_context_mapper_build_global_mapping() -> None:
    """Test global mapping generation across None, empty string, and valid execution_id."""
    assert ContextMapper.build_global_mapping(execution_id=None) == ""
    assert ContextMapper.build_global_mapping(execution_id="") == ""
    mapping = ContextMapper.build_global_mapping(execution_id="exec_123")
    assert "Execution ID: exec_123" in mapping

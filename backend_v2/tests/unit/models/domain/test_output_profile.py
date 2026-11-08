"""Unit tests for OutputProfile domain model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.output_profile import (
    STANDARD_MATRIX_VISIBLE_COLUMNS,
    OutputProfile,
)
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.enums import (
    DisplayScale,
    EntityPrefix,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.tests.factories.model_factories import OutputProfileFactory

__all__ = [
    "test_output_profile_custom_scale_bounds",
    "test_output_profile_invalid_id_and_extra_forbid_failure",
    "test_output_profile_invalid_matrix_visible_columns",
    "test_output_profile_length_and_extension_bva",
    "test_output_profile_matrix_graphs_coherence",
    "test_output_profile_matrix_group_ids_unique",
    "test_output_profile_minimal_valid",
    "test_output_profile_synthesis_properties",
    "test_output_profile_variance_validation_requires_target_block",
]


def test_output_profile_minimal_valid() -> None:
    """Verify valid OutputProfile instantiation via OutputProfileFactory and default properties."""
    profile = OutputProfileFactory.build(
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        matrix_visible_columns=list(STANDARD_MATRIX_VISIBLE_COLUMNS),
        content_blocks=[],
    )
    assert profile.id.startswith(f"{EntityPrefix.OUTPUT_PROFILE.value}_")
    assert profile.requires_executive_synthesis is False
    assert profile.requires_group_synthesis is False
    assert profile.requires_row_explanations is True
    assert profile.is_synthesis_expected is True


def test_output_profile_variance_validation_requires_target_block() -> None:
    """Verify Fail-Fast validation when variance validation is active without variance_target_block."""
    with pytest.raises(ValidationError, match="variance_target_block"):
        OutputProfileFactory.build(
            target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
            variance_target_block=None,
            content_blocks=[],
        )

    with pytest.raises(ValidationError, match="variance_target_block"):
        OutputProfileFactory.build(
            target_block_order=[TargetBlockType.METADATA_BLOCK],
            visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
            variance_target_block=None,
            content_blocks=[],
        )

    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    profile = OutputProfileFactory.build(
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
        variance_target_block=block_id,
        content_blocks=[],
    )
    assert profile.variance_target_block == block_id


def test_output_profile_matrix_graphs_coherence() -> None:
    """Verify Fail-Fast validation when MATRIX_GRAPHS_BLOCK has empty matrix_synthesis_groups."""
    with pytest.raises(ValidationError, match="matrix_synthesis_groups is empty"):
        OutputProfileFactory.build(
            target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
            matrix_synthesis_groups=[],
            content_blocks=[],
        )

    grp = MatrixSynthesisGroup(
        id=generate_opaque_id(EntityPrefix.SYNTHESIS_GROUP),
        title=I18nText(translations={"en": "Group 1"}),
        target_blocks=[generate_opaque_id(EntityPrefix.PROMPT_BLOCK)],
    )
    profile = OutputProfileFactory.build(
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
        matrix_synthesis_groups=[grp],
        content_blocks=[],
    )
    assert len(profile.matrix_synthesis_groups) == 1
    assert profile.requires_group_synthesis is True


def test_output_profile_custom_scale_bounds() -> None:
    """Verify ISTQB boundary value validation for DisplayScale.CUSTOM min/max bounds."""
    with pytest.raises(ValidationError, match="custom_scale_min and custom_scale_max are required"):
        OutputProfileFactory.build(
            display_scale=DisplayScale.CUSTOM,
            custom_scale_min=None,
            custom_scale_max=None,
            content_blocks=[],
        )

    with pytest.raises(ValidationError, match="must be strictly greater"):
        OutputProfileFactory.build(
            display_scale=DisplayScale.CUSTOM,
            custom_scale_min=5.0,
            custom_scale_max=5.0,
            content_blocks=[],
        )

    with pytest.raises(ValidationError, match="must be strictly greater"):
        OutputProfileFactory.build(
            display_scale=DisplayScale.CUSTOM,
            custom_scale_min=5.0,
            custom_scale_max=3.0,
            content_blocks=[],
        )

    profile = OutputProfileFactory.build(
        display_scale=DisplayScale.CUSTOM,
        custom_scale_min=1.0,
        custom_scale_max=10.0,
        content_blocks=[],
    )
    assert profile.custom_scale_min == 1.0
    assert profile.custom_scale_max == 10.0


def test_output_profile_matrix_group_ids_unique() -> None:
    """Verify Fail-Fast rejection of duplicate MatrixSynthesisGroup IDs."""
    shared_grp_id = generate_opaque_id(EntityPrefix.SYNTHESIS_GROUP)
    grp1 = MatrixSynthesisGroup(
        id=shared_grp_id,
        title=I18nText(translations={"en": "Group 1"}),
        target_blocks=[generate_opaque_id(EntityPrefix.PROMPT_BLOCK)],
    )
    grp2 = MatrixSynthesisGroup(
        id=shared_grp_id,
        title=I18nText(translations={"en": "Group 2"}),
        target_blocks=[generate_opaque_id(EntityPrefix.PROMPT_BLOCK)],
    )
    with pytest.raises(ValidationError, match="Duplicate synthesis group IDs"):
        OutputProfileFactory.build(
            target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
            matrix_synthesis_groups=[grp1, grp2],
            content_blocks=[],
        )


def test_output_profile_synthesis_properties() -> None:
    """Verify synthesis expectation computed properties across block and column configurations."""
    profile = OutputProfileFactory.build(
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
        matrix_visible_columns=["label", "raw_score"],
        content_blocks=[],
    )
    assert profile.requires_executive_synthesis is True
    assert profile.requires_row_explanations is False
    assert profile.is_synthesis_expected is True

    profile_none = OutputProfileFactory.build(
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        matrix_visible_columns=[],
        content_blocks=[],
    )
    assert profile_none.requires_row_explanations is False
    assert profile_none.is_synthesis_expected is False


def test_output_profile_invalid_matrix_visible_columns() -> None:
    """Verify Fail-Fast rejection of unknown ReportMatrixColumn identifiers."""
    with pytest.raises(ValidationError):
        OutputProfileFactory.build(
            matrix_visible_columns=["label", "unknown_column_key"],
            content_blocks=[],
        )


def test_output_profile_length_and_extension_bva() -> None:
    """Verify ISTQB boundary value analysis on integer length and extension constraints."""
    # Valid exact boundaries
    valid_min = OutputProfileFactory.build(
        max_extension_items=1,
        synthesis_length_constraint=100,
        row_explanation_length_constraint=50,
        content_blocks=[],
    )
    assert valid_min.max_extension_items == 1
    assert valid_min.synthesis_length_constraint == 100

    valid_max = OutputProfileFactory.build(
        max_extension_items=100,
        synthesis_length_constraint=5000,
        row_explanation_length_constraint=1000,
        content_blocks=[],
    )
    assert valid_max.max_extension_items == 100
    assert valid_max.synthesis_length_constraint == 5000

    # Invalid min - 1 and max + 1 boundaries
    with pytest.raises(ValidationError):
        OutputProfileFactory.build(max_extension_items=0, content_blocks=[])

    with pytest.raises(ValidationError):
        OutputProfileFactory.build(max_extension_items=101, content_blocks=[])

    with pytest.raises(ValidationError):
        OutputProfileFactory.build(synthesis_length_constraint=99, content_blocks=[])

    with pytest.raises(ValidationError):
        OutputProfileFactory.build(synthesis_length_constraint=5001, content_blocks=[])


def test_output_profile_invalid_id_and_extra_forbid_failure() -> None:
    """Verify OPAQUE_STRIPE_ID_REGEX enforcement and extra='forbid' rejection."""
    with pytest.raises(ValidationError):
        OutputProfileFactory.build(id="invalid_non_opaque_id", content_blocks=[])

    valid_dump = OutputProfileFactory.build(content_blocks=[]).model_dump(mode="json")
    valid_dump["unexpected_rogue_field"] = "forbidden"
    with pytest.raises(ValidationError):
        OutputProfile.model_validate(valid_dump)

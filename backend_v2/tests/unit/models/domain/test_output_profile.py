"""Unit tests for OutputProfile domain model."""

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.enums import DisplayScale, TargetBlockType, XaiExtensionType


def _make_base_profile(**kwargs: object) -> OutputProfile:
    data = {
        "id": "pro_1234567890abcdef",
        "slug": "exec_profile",
        "workflow_id": "wor_1234567890abcdef",
        "name": {"translations": {"en": "Executive Profile"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK.value],
    }
    data.update(kwargs)
    return OutputProfile.model_validate(data)


def _make_base_profile_data(**kwargs: object):
    data = {
        "id": "pro_1234567890abcdef",
        "slug": "exec_profile",
        "workflow_id": "wor_1234567890abcdef",
        "name": {"translations": {"en": "Executive Profile"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK.value],
    }
    data.update(kwargs)
    return data


def test_output_profile_minimal_valid() -> None:
    profile = _make_base_profile()
    assert profile.id == "pro_1234567890abcdef"
    assert profile.slug == "exec_profile"
    assert profile.requires_executive_synthesis is False
    assert profile.requires_group_synthesis is False
    assert profile.requires_row_explanations is True
    assert profile.is_synthesis_expected is True


def test_output_profile_variance_validation_requires_target_block() -> None:
    # TargetBlockType.VARIANCE_VALIDATION_BLOCK without variance_target_block raises ValueError
    data = _make_base_profile_data(
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK.value],
        variance_target_block=None,
    )
    with pytest.raises(ValueError, match="variance_target_block"):
        OutputProfile.model_validate(data)

    # Extension without variance_target_block raises ValueError
    data_ext = _make_base_profile_data(
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION.value],
        variance_target_block=None,
    )
    with pytest.raises(ValueError, match="variance_target_block"):
        OutputProfile.model_validate(data_ext)

    # Sized variance_target_block succeeds
    profile = _make_base_profile(
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK.value],
        variance_target_block="blk_0123456789abcdef",
    )
    assert profile.variance_target_block == "blk_0123456789abcdef"


def test_output_profile_matrix_graphs_coherence() -> None:
    data = _make_base_profile_data(
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK.value],
        matrix_synthesis_groups=[],
    )
    with pytest.raises(ValueError, match="matrix_synthesis_groups is empty"):
        OutputProfile.model_validate(data)

    grp = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=I18nText(translations={"en": "Group 1"}),
        target_blocks=["blk_1234567890abcdef"],
    )
    profile = _make_base_profile(
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK.value],
        matrix_synthesis_groups=[grp.model_dump(mode="json")],
    )
    assert len(profile.matrix_synthesis_groups) == 1
    assert profile.requires_group_synthesis is True


def test_output_profile_custom_scale_bounds() -> None:
    # CUSTOM scale without bounds
    data_missing = _make_base_profile_data(
        display_scale=DisplayScale.CUSTOM.value,
        custom_scale_min=None,
        custom_scale_max=None,
    )
    with pytest.raises(ValueError, match="custom_scale_min and custom_scale_max are required"):
        OutputProfile.model_validate(data_missing)

    # CUSTOM scale with max <= min
    data_invalid = _make_base_profile_data(
        display_scale=DisplayScale.CUSTOM.value,
        custom_scale_min=5.0,
        custom_scale_max=3.0,
    )
    with pytest.raises(ValueError, match="must be strictly greater"):
        OutputProfile.model_validate(data_invalid)

    # Valid bounds
    profile = _make_base_profile(
        display_scale=DisplayScale.CUSTOM.value,
        custom_scale_min=1.0,
        custom_scale_max=10.0,
    )
    assert profile.custom_scale_min == 1.0
    assert profile.custom_scale_max == 10.0


def test_output_profile_matrix_group_ids_unique() -> None:
    grp1 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=I18nText(translations={"en": "Group 1"}),
        target_blocks=["blk_1234567890abcdef"],
    )
    grp2 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=I18nText(translations={"en": "Group 2"}),
        target_blocks=["blk_1234567890abcdef"],
    )
    data = _make_base_profile_data(
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK.value],
        matrix_synthesis_groups=[grp1.model_dump(mode="json"), grp2.model_dump(mode="json")],
    )
    with pytest.raises(ValueError, match="Duplicate synthesis group IDs"):
        OutputProfile.model_validate(data)


def test_output_profile_synthesis_properties() -> None:
    profile = _make_base_profile(
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value],
        matrix_visible_columns=["label", "raw_score"],
    )
    assert profile.requires_executive_synthesis is True
    assert profile.requires_row_explanations is False
    assert profile.is_synthesis_expected is True

    # No synthesis at all
    profile_none = _make_base_profile(
        target_block_order=[TargetBlockType.METADATA_BLOCK.value],
        matrix_visible_columns=[],
    )
    assert profile_none.is_synthesis_expected is False

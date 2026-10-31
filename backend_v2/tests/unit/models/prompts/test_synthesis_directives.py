"""Unit tests for synthesis prompt directives and factory defaults."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix, TargetBlockType
from backend_v2.models.prompts.synthesis.synthesis_directives import (
    CAUSAL_TDA_DIAGNOSIS_MANDATE,
    CONTRASTIVE_FRONTIER_MANDATE,
    EXECUTIVE_SUMMARY_SECTION_ID,
    EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX,
    ROW_EXPLANATION_SYSTEM_PROMPT,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_SYSTEM_PROMPT,
    SYNTHESIS_XAI_CURATION,
    VARIANCE_SYSTEM_PROMPT,
)
from backend_v2.services.factories.output_profile_factory import (
    DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE,
    DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE,
    DEFAULT_FACTORY_TONE_INSTRUCTION,
    DEFAULT_FACTORY_VARIANCE_DIRECTIVE,
    DEFAULT_FACTORY_XAI_DIRECTIVE,
    build_draft_output_profile,
)

__all__ = [
    "test_build_draft_output_profile_rejects_blank_initial_target_block",
    "test_build_draft_output_profile_rejects_invalid_profile_id",
    "test_executive_summary_section_id_ssot_parity",
    "test_factory_default_directives_are_valid_strings",
    "test_length_budget_mandate_presence_and_brevity_mandate_absence",
    "test_synthesis_system_prompts_content",
]


def test_executive_summary_section_id_ssot_parity() -> None:
    """Verify EXECUTIVE_SUMMARY_SECTION_ID strictly matches TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value."""
    assert EXECUTIVE_SUMMARY_SECTION_ID == "executive_summary_block"
    assert EXECUTIVE_SUMMARY_SECTION_ID == TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value


def test_synthesis_system_prompts_content() -> None:
    """Verify system prompts and static XML mandates have substantive instructions."""
    assert "Strategic Report Evaluator" in SYNTHESIS_SYSTEM_PROMPT
    assert "Forensic Evidence Analyst" in ROW_EXPLANATION_SYSTEM_PROMPT
    assert "Cognitive Evaluator" in VARIANCE_SYSTEM_PROMPT
    assert "<causal_tda_diagnosis_mandate>" in CAUSAL_TDA_DIAGNOSIS_MANDATE
    assert "</causal_tda_diagnosis_mandate>" in CAUSAL_TDA_DIAGNOSIS_MANDATE
    assert "<contrastive_frontier_mandate>" in CONTRASTIVE_FRONTIER_MANDATE
    assert "</contrastive_frontier_mandate>" in CONTRASTIVE_FRONTIER_MANDATE
    assert "<xai_curation_mandate>" in SYNTHESIS_XAI_CURATION
    assert "<section_rules>" in SYNTHESIS_SECTION_RULES_PREFIX


def test_factory_default_directives_are_valid_strings() -> None:
    """Verify all factory default directives are non-empty strings with content."""
    directives = [
        DEFAULT_FACTORY_TONE_INSTRUCTION,
        DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE,
        DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE,
        DEFAULT_FACTORY_XAI_DIRECTIVE,
        DEFAULT_FACTORY_VARIANCE_DIRECTIVE,
    ]
    for d in directives:
        assert isinstance(d, str)
        assert len(d.strip()) > 0


def test_length_budget_mandate_presence_and_brevity_mandate_absence() -> None:
    """Verify LENGTH BUDGET MANDATE is present and CRITICAL BREVITY MANDATE is eradicated."""
    assert "LENGTH BUDGET MANDATE" in SYNTHESIS_SECTION_RULES_PREFIX
    assert "CRITICAL BREVITY MANDATE" not in SYNTHESIS_SECTION_RULES_PREFIX
    assert "2-3 short sentences" not in SYNTHESIS_SECTION_RULES_PREFIX

    assert "LENGTH BUDGET MANDATE" in EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX
    assert "CRITICAL BREVITY MANDATE" not in EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX
    assert "2-3 short sentences" not in EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX


def test_build_draft_output_profile_rejects_invalid_profile_id() -> None:
    """Verify build_draft_output_profile raises AppException on malformed profile_id."""
    workflow_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    with pytest.raises(AppException) as exc_info:
        build_draft_output_profile(profile_id="invalid_id", workflow_id=workflow_id)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_build_draft_output_profile_rejects_blank_initial_target_block() -> None:
    """Verify build_draft_output_profile raises AppException when initial_target_block is whitespace."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    workflow_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    with pytest.raises(AppException) as exc_info:
        build_draft_output_profile(
            profile_id=profile_id,
            workflow_id=workflow_id,
            initial_target_block="   ",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

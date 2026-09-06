"""Unit tests for synthesis prompt directives and factory defaults."""

import xml.etree.ElementTree as ET

from backend_v2.models.enums import TargetBlockType
from backend_v2.models.prompts.synthesis.synthesis_directives import (
    DEFAULT_ROW_EXPLANATION_SYSTEM_PROMPT,
    DEFAULT_SYNTHESIS_SYSTEM_PROMPT,
    DEFAULT_VARIANCE_SYSTEM_PROMPT,
    EXECUTIVE_SUMMARY_SECTION_ID,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_XAI_CURATION,
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
)


def test_executive_summary_section_id_ssot_parity() -> None:
    """Verify EXECUTIVE_SUMMARY_SECTION_ID strictly matches TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value."""
    assert EXECUTIVE_SUMMARY_SECTION_ID == "executive_summary_block"
    assert EXECUTIVE_SUMMARY_SECTION_ID == TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value


def test_default_synthesis_prompts_content() -> None:
    """Verify default system prompts have substantive instructions."""
    assert "Senior Executive Coach" in DEFAULT_SYNTHESIS_SYSTEM_PROMPT
    assert "Forensic Evidence Analyst" in DEFAULT_ROW_EXPLANATION_SYSTEM_PROMPT
    assert "Cognitive Evaluator" in DEFAULT_VARIANCE_SYSTEM_PROMPT
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

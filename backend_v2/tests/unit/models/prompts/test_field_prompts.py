"""Unit tests for the centralized field prompts module.

Ensures strict 1:1 File-to-Test matching mandate of the Universal Quality Gate.
"""

from backend_v2.models.prompts.execution.field_prompts import (
    DESC_CONTEXTUAL_OVERRIDE,
    DESC_EVALUATION_NOTES,
    DESC_EXACT_QUOTES,
    DESC_REASONING_TRACE,
    DESC_SEMANTIC_REASONING,
    STRICT_JSON_STRUCTURE_MANDATE,
    XAI_DESC_CITATION,
    XAI_DESC_COACHING,
    XAI_DESC_CONFIDENCE,
    XAI_DESC_FALSIFICATION,
    XAI_DESC_JUSTIFICATION,
)


def test_field_prompts_constants() -> None:
    """Verify core field prompt constants are non-empty strings."""
    assert isinstance(DESC_EXACT_QUOTES, str) and len(DESC_EXACT_QUOTES) > 0
    assert isinstance(DESC_CONTEXTUAL_OVERRIDE, str) and len(DESC_CONTEXTUAL_OVERRIDE) > 0
    assert isinstance(DESC_SEMANTIC_REASONING, str) and len(DESC_SEMANTIC_REASONING) > 0
    assert isinstance(DESC_REASONING_TRACE, str) and len(DESC_REASONING_TRACE) > 0
    assert isinstance(DESC_EVALUATION_NOTES, str) and len(DESC_EVALUATION_NOTES) > 0
    assert "<json_structure_mandate>" in STRICT_JSON_STRUCTURE_MANDATE


def test_xai_field_descriptions() -> None:
    """Verify XAI extension template descriptions are format-ready strings."""
    assert "{block_id}" in XAI_DESC_JUSTIFICATION
    assert "{block_id}" in XAI_DESC_CITATION
    assert "{block_id}" in XAI_DESC_FALSIFICATION
    assert isinstance(XAI_DESC_COACHING, str) and len(XAI_DESC_COACHING) > 0
    assert isinstance(XAI_DESC_CONFIDENCE, str) and len(XAI_DESC_CONFIDENCE) > 0

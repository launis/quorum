"""Unit tests for the centralized field prompts module.

Ensures strict 1:1 File-to-Test matching mandate of the Universal Quality Gate.
"""

from backend_v2.models.prompts.execution.field_prompts import (
    DESC_ALIAS,
    DESC_COACHING,
    DESC_CONTEXTUAL_OVERRIDE,
    DESC_EVALUATION_NOTES,
    DESC_EXACT_QUOTE_TEXT,
    DESC_EXACT_QUOTES,
    DESC_FALSIFICATION,
    DESC_IS_TRUE,
    DESC_REASONING_TRACE,
    DESC_REMEDIATION_STEPS,
    DESC_SEMANTIC_REASONING,
    DESC_SOURCE_QUOTE,
    STRICT_JSON_STRUCTURE_MANDATE,
    XAI_DESC_CITATION,
    XAI_DESC_COACHING,
    XAI_DESC_CONFIDENCE,
    XAI_DESC_EMOTIONAL_SENTIMENT,
    XAI_DESC_FALSIFICATION,
    XAI_DESC_JUSTIFICATION,
    XAI_DESC_MISSING_CONTEXT,
    XAI_DESC_REMEDIATION_STEPS,
    XAI_DESC_RISK_FLAG,
    XAI_DESC_THEORY_LINK,
)


def test_field_prompts_constants() -> None:
    """Verify core field prompt constants are non-empty strings."""
    assert isinstance(DESC_ALIAS, str) and len(DESC_ALIAS) > 0
    assert isinstance(DESC_IS_TRUE, str) and len(DESC_IS_TRUE) > 0
    assert isinstance(DESC_EXACT_QUOTES, str) and len(DESC_EXACT_QUOTES) > 0
    assert isinstance(DESC_EXACT_QUOTE_TEXT, str) and len(DESC_EXACT_QUOTE_TEXT) > 0
    assert isinstance(DESC_CONTEXTUAL_OVERRIDE, str) and len(DESC_CONTEXTUAL_OVERRIDE) > 0
    assert isinstance(DESC_SEMANTIC_REASONING, str) and len(DESC_SEMANTIC_REASONING) > 0
    assert isinstance(DESC_SOURCE_QUOTE, str) and len(DESC_SOURCE_QUOTE) > 0
    assert isinstance(DESC_COACHING, str) and len(DESC_COACHING) > 0
    assert isinstance(DESC_FALSIFICATION, str) and len(DESC_FALSIFICATION) > 0
    assert isinstance(DESC_REMEDIATION_STEPS, str) and len(DESC_REMEDIATION_STEPS) > 0
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
    assert isinstance(XAI_DESC_MISSING_CONTEXT, str) and len(XAI_DESC_MISSING_CONTEXT) > 0
    assert isinstance(XAI_DESC_RISK_FLAG, str) and len(XAI_DESC_RISK_FLAG) > 0
    assert isinstance(XAI_DESC_REMEDIATION_STEPS, str) and len(XAI_DESC_REMEDIATION_STEPS) > 0
    assert isinstance(XAI_DESC_EMOTIONAL_SENTIMENT, str) and len(XAI_DESC_EMOTIONAL_SENTIMENT) > 0
    assert isinstance(XAI_DESC_THEORY_LINK, str) and len(XAI_DESC_THEORY_LINK) > 0

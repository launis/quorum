"""Unit tests for the centralized LLM architectural directives."""

from backend_v2.llm.directives import (
    EPISTEMIC_GLOSSARY_MANDATE,
    SEMANTIC_BLEED_MANDATE,
)


def test_directives_existence() -> None:
    """Verify that steering directives are defined and contain necessary content."""
    assert SEMANTIC_BLEED_MANDATE is not None
    assert "CRITICAL PROMPT SAFETY" in SEMANTIC_BLEED_MANDATE
    assert "extract evidence quotes" in SEMANTIC_BLEED_MANDATE

    assert EPISTEMIC_GLOSSARY_MANDATE is not None
    assert "<EPISTEMIC_GLOSSARY>" in EPISTEMIC_GLOSSARY_MANDATE
    assert "Empirical Data" in EPISTEMIC_GLOSSARY_MANDATE
    assert "Formal Model" in EPISTEMIC_GLOSSARY_MANDATE

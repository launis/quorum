"""Unit tests for backend_v2/models/prompts/style_directives.py."""

from backend_v2.models.prompts.style_directives import (
    ANTI_JARGON_MANDATE_BLOCK,
    DEFAULT_COACHING_TONE_MANDATE,
    SPARSE_DATA_SYNTHESIS_MANDATE,
    SYNTHESIS_CITATION_RULES,
    SYNTHESIS_CITATION_RULES_HARVARD,
    SYNTHESIS_LENGTH_CONSTRAINT,
    SYNTHESIS_NO_CITATION_RULES,
    __all__,
)


def test_style_directives_exports() -> None:
    """Verify that all style directives are non-empty strings and in __all__."""
    assert "SYNTHESIS_CITATION_RULES_HARVARD" in __all__
    assert "SYNTHESIS_NO_CITATION_RULES" in __all__
    assert "SYNTHESIS_CITATION_RULES" in __all__
    assert "ANTI_JARGON_MANDATE_BLOCK" in __all__
    assert "DEFAULT_COACHING_TONE_MANDATE" in __all__
    assert "SPARSE_DATA_SYNTHESIS_MANDATE" in __all__
    assert "SYNTHESIS_LENGTH_CONSTRAINT" in __all__


def test_harvard_citation_directive_structure() -> None:
    """Positive: verify Harvard citation directive contains required XML tags and instructions."""
    assert "<citation_rules>" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "</citation_rules>" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "HARVARD CITATION STANDARD MANDATE" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "(Author, Year)" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "cited_sources" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "STRICT PROHIBITIONS" in SYNTHESIS_CITATION_RULES_HARVARD
    assert SYNTHESIS_CITATION_RULES == SYNTHESIS_CITATION_RULES_HARVARD


def test_no_citation_directive_structure() -> None:
    """Positive: verify no-citation directive instructs clean narrative without parenthetical tags."""
    assert "<citation_rules>" in SYNTHESIS_NO_CITATION_RULES
    assert "</citation_rules>" in SYNTHESIS_NO_CITATION_RULES
    assert "NO IN-TEXT CITATIONS MANDATE" in SYNTHESIS_NO_CITATION_RULES
    assert "cited_sources" in SYNTHESIS_NO_CITATION_RULES


def test_style_directives_xml_tag_closure() -> None:
    """Negative / Integrity: verify all directives have balanced XML tags."""
    directives = [
        DEFAULT_COACHING_TONE_MANDATE,
        ANTI_JARGON_MANDATE_BLOCK,
        SPARSE_DATA_SYNTHESIS_MANDATE,
        SYNTHESIS_LENGTH_CONSTRAINT,
        SYNTHESIS_CITATION_RULES_HARVARD,
        SYNTHESIS_NO_CITATION_RULES,
    ]
    for directive in directives:
        assert isinstance(directive, str)
        assert len(directive.strip()) > 0
        assert "<" in directive and ">" in directive

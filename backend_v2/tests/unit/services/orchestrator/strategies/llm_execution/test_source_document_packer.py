"""Unit tests for SourceDocumentPacker."""

import re

from backend_v2.models.core_base import I18nText
from backend_v2.models.v2_core import ExpectedInput
from backend_v2.services.orchestrator.strategies.llm_execution.source_document_packer import SourceDocumentPacker


def _build_expected_input(key: str, ai_desc: str | None = None) -> ExpectedInput:
    """Helper to instantiate ExpectedInput with required strict fields."""
    return ExpectedInput(
        input_key=key,
        label=I18nText(translations={"en": f"Label {key}"}),
        required=True,
        input_modes=["paste"],
        description=I18nText(translations={"en": f"Description {key}"}),
        ai_description=ai_desc,
    )


def test_source_document_packer_multi_document_with_metadata() -> None:
    """Verify multi-document dictionary packing with inline ai_context_directive tags."""
    inputs = {
        "chat_log": "User: Hello\nCoach: Welcome to the session.",
        "product_text": "Executive summary and strategic recommendations.",
    }
    expected_inputs = [
        _build_expected_input("chat_log", "Dialogue between executive coach and candidate."),
        _build_expected_input("product_text", "Final deliverable document written by candidate."),
    ]

    packed = SourceDocumentPacker.pack(inputs, expected_inputs)

    assert (
        '<ai_context_directive document="chat_log">'
        "Dialogue between executive coach and candidate.</ai_context_directive>" in packed
    )
    assert "User: Hello\nCoach: Welcome to the session." in packed
    assert (
        '<ai_context_directive document="product_text">'
        "Final deliverable document written by candidate.</ai_context_directive>" in packed
    )
    assert "Executive summary and strategic recommendations." in packed


def test_source_document_packer_single_string_passthrough() -> None:
    """Verify single string payloads pass through without wrapping."""
    raw_text = "   This is a standalone single document.   "
    packed = SourceDocumentPacker.pack(raw_text)
    assert packed == "This is a standalone single document."
    assert "<ai_context_directive" not in packed


def test_source_document_packer_missing_metadata() -> None:
    """Verify documents are packed without directives if expected_inputs is None or lacks descriptions."""
    inputs = {
        "doc1": "Content 1",
        "doc2": "Content 2",
    }
    # Case A: expected_inputs is None
    packed_none = SourceDocumentPacker.pack(inputs, None)
    assert packed_none == "Content 1\n\nContent 2"
    assert "<ai_context_directive" not in packed_none

    # Case B: expected_inputs has None or whitespace ai_description
    expected_inputs = [
        _build_expected_input("doc1", None),
        _build_expected_input("doc2", "   "),
    ]
    packed_empty_desc = SourceDocumentPacker.pack(inputs, expected_inputs)
    assert packed_empty_desc == "Content 1\n\nContent 2"
    assert "<ai_context_directive" not in packed_empty_desc


def test_source_document_packer_istqb_negatives() -> None:
    """Verify ISTQB negative partitions: falsy inputs, invalid types, non-string dictionary values."""
    # Falsy inputs
    assert SourceDocumentPacker.pack(None) == ""
    assert SourceDocumentPacker.pack("") == ""
    assert SourceDocumentPacker.pack("   ") == ""
    assert SourceDocumentPacker.pack({}) == ""

    # Invalid primitive / collection types
    assert SourceDocumentPacker.pack(12345) == ""
    assert SourceDocumentPacker.pack(3.14) == ""
    assert SourceDocumentPacker.pack(True) == ""
    assert SourceDocumentPacker.pack(["doc1", "doc2"]) == ""

    # Dictionary with non-string, whitespace, or empty values
    inputs_with_garbage = {
        "valid_key": "Valid substantive content.",
        "none_key": None,
        "empty_key": "",
        "whitespace_key": "   \n\t  ",
        "int_key": 999,
        "list_key": ["should", "be", "skipped"],
    }
    packed = SourceDocumentPacker.pack(inputs_with_garbage)
    assert packed == "Valid substantive content."


def test_source_document_packer_survives_tda_paragraph_split() -> None:
    r"""Verify that split('\n\n') produces intact blocks without broken XML boundary tags."""
    inputs = {
        "chat_log": "Paragraph 1 of chat.\n\nParagraph 2 of chat.",
        "reflection_text": "Single paragraph reflection.",
    }
    expected_inputs = [
        _build_expected_input("chat_log", "Process coaching dialogue."),
        _build_expected_input("reflection_text", "Retrospective self-assessment."),
    ]

    packed = SourceDocumentPacker.pack(inputs, expected_inputs)
    paragraphs = [p.strip() for p in packed.split("\n\n") if p.strip()]

    # Verify paragraph count and structure:
    # 1. <ai_context_directive document="chat_log">...
    # 2. Paragraph 1 of chat.
    # 3. Paragraph 2 of chat.
    # 4. <ai_context_directive document="reflection_text">...
    # 5. Single paragraph reflection.
    assert len(paragraphs) == 5

    # Each directive MUST be completely self-contained within its own single paragraph block
    directive_paragraphs = [p for p in paragraphs if "<ai_context_directive" in p]
    assert len(directive_paragraphs) == 2

    for dp in directive_paragraphs:
        assert dp.startswith("<ai_context_directive document=")
        assert dp.endswith("</ai_context_directive>")
        open_tags = re.findall(r"<ai_context_directive[^>]*>", dp)
        close_tags = re.findall(r"</ai_context_directive>", dp)
        assert len(open_tags) == 1
        assert len(close_tags) == 1

    # Content paragraphs MUST NOT contain orphaned XML tags
    content_paragraphs = [p for p in paragraphs if "<ai_context_directive" not in p]
    assert len(content_paragraphs) == 3
    for cp in content_paragraphs:
        assert "<" not in cp
        assert ">" not in cp

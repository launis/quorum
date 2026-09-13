"""Unit tests for SourceDocumentPacker."""

import re
from typing import Any

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.state import StepOutputDTO
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

    # Invalid primitive / collection types raise fail-fast AppException
    for invalid_val in [12345, 3.14, True, ["doc1", "doc2"]]:
        with pytest.raises(AppException) as exc_info:
            SourceDocumentPacker.pack(invalid_val)
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

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


def test_source_document_packer_step_scoping_and_allowed_keys() -> None:
    """Verify resolve_allowed_keys resolution and pack() key filtering according to step contracts."""
    # 1. resolve_allowed_keys canonical $inputs.<key> resolution
    mappings = {
        "text": "$inputs.product_text",
        "chat": "$inputs.chat_log",
        "nested": "$inputs.assignment_brief",
    }
    assert SourceDocumentPacker.resolve_allowed_keys(mappings) == {
        "product_text",
        "chat_log",
        "assignment_brief",
    }

    # 2. $steps and $steps.<step_id> mappings are resolved into allowed keys
    step_mappings = {
        "prior_1": "$steps.node_1",
        "prior_2": "$steps.node_2.output",
        "raw_step": "$steps",
    }
    assert SourceDocumentPacker.resolve_allowed_keys(step_mappings) == {
        "$steps.node_1",
        "$steps.node_2.output",
        "$steps",
    }

    # Mixed mappings
    mixed = {
        "doc": "$inputs.target_doc",
        "step": "$steps.previous",
    }
    assert SourceDocumentPacker.resolve_allowed_keys(mixed) == {"target_doc", "$steps.previous"}

    # 3. Empty or None mappings yield empty set
    assert SourceDocumentPacker.resolve_allowed_keys({}) == set()
    assert SourceDocumentPacker.resolve_allowed_keys(None) == set()

    # 4. pack with allowed_keys excluding unmapped inputs
    inputs = {
        "product_text": "Substantive memo text.",
        "chat_log": "Dialogue to be excluded.",
        "extra_doc": "Extra unmapped document.",
    }
    expected_inputs = [
        _build_expected_input("product_text", "Executive memo description."),
        _build_expected_input("chat_log", "Dialogue description."),
    ]
    packed = SourceDocumentPacker.pack(inputs, expected_inputs, allowed_keys={"product_text"})
    assert "Substantive memo text." in packed
    assert '<ai_context_directive document="product_text">' in packed
    assert "Dialogue to be excluded." not in packed
    assert "chat_log" not in packed
    assert "Extra unmapped document." not in packed

    # 5. pack with empty allowed_keys set() returns empty string for both dict and str payloads
    assert SourceDocumentPacker.pack(inputs, expected_inputs, allowed_keys=set()) == ""
    assert SourceDocumentPacker.pack("Standalone raw document", allowed_keys=set()) == ""

    # Non-existent key in allowed_keys yields empty string
    assert SourceDocumentPacker.pack(inputs, expected_inputs, allowed_keys={"non_existent_key"}) == ""


def test_source_document_packer_step_outputs_packing_positive() -> None:
    """Positive: assert packing steps with $steps mappings emits non-empty source text with <step_output> headers."""
    step_outputs = [
        StepOutputDTO(
            step_id="sr_step_1",
            block_id="blk_1",
            data_type="text",
            payload="First stage analysis summary.",
        ),
        StepOutputDTO(
            step_id="sr_step_2",
            block_id="blk_2",
            data_type="text",
            payload="Second stage evaluation findings.",
        ),
        StepOutputDTO(
            step_id="inputs",
            block_id="inputs",
            data_type="unknown",
            payload={"raw": "initial"},
        ),
    ]

    # Wildcard $steps packing
    packed = SourceDocumentPacker.pack(
        inputs_payload=None,
        allowed_keys={"$steps"},
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_step_1">' in packed
    assert "First stage analysis summary." in packed
    assert '<step_output step_id="sr_step_2">' in packed
    assert "Second stage evaluation findings." in packed
    assert "inputs" not in packed

    # Specific step targeting $steps.sr_step_1
    packed_single = SourceDocumentPacker.pack(
        inputs_payload=None,
        allowed_keys={"$steps.sr_step_1"},
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_step_1">' in packed_single
    assert "First stage analysis summary." in packed_single
    assert '<step_output step_id="sr_step_2">' not in packed_single

    # Mixed inputs + step outputs
    inputs = {"memo": "Candidate deliverable text"}
    packed_mixed = SourceDocumentPacker.pack(
        inputs_payload=inputs,
        allowed_keys={"memo", "$steps.sr_step_2"},
        step_outputs=step_outputs,
    )
    assert "Candidate deliverable text" in packed_mixed
    assert '<step_output step_id="sr_step_2">' in packed_mixed
    assert "Second stage evaluation findings." in packed_mixed
    assert "sr_step_1" not in packed_mixed


def test_source_document_packer_non_existent_step_reference_fails_fast() -> None:
    """Negative Partition 2: assert unmapped or non-existent step references fail fast without fallback."""
    step_outputs = [
        StepOutputDTO(
            step_id="sr_existing",
            block_id="blk_1",
            data_type="text",
            payload="Existing step output.",
        ),
    ]

    with pytest.raises(AppException) as exc_info:
        SourceDocumentPacker.pack(
            inputs_payload=None,
            allowed_keys={"$steps.sr_nonexistent"},
            step_outputs=step_outputs,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name
    assert "sr_nonexistent" in exc_info.value.message


def test_source_document_packer_structured_dict_payload_and_edge_cases() -> None:
    """Test structured payload dictionary parsing, non-string mappings, and invalid items."""
    # 1. Non-string value in input_mappings
    mappings: dict[str, Any] = {"doc": "$inputs.valid", "bad": 12345}
    assert SourceDocumentPacker.resolve_allowed_keys(mappings) == {"valid"}

    # 2. Structured dict payloads in step_outputs (text, markdown, content, and empty)
    step_outputs = [
        StepOutputDTO(
            step_id="sr_text",
            block_id="blk_t",
            data_type="text",
            payload={"text": "Text payload field"},
        ),
        StepOutputDTO(
            step_id="sr_md",
            block_id="blk_m",
            data_type="text",
            payload={"markdown": "Markdown payload field"},
        ),
        StepOutputDTO(
            step_id="sr_cnt",
            block_id="blk_c",
            data_type="text",
            payload={"content": "Content payload field"},
        ),
        StepOutputDTO(
            step_id="sr_nontext",
            block_id="blk_n",
            data_type="text",
            payload={"other": 12345},
        ),
    ]

    packed = SourceDocumentPacker.pack(
        allowed_keys={"$steps"},
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_text">' in packed
    assert "Text payload field" in packed
    assert '<step_output step_id="sr_md">' in packed
    assert "Markdown payload field" in packed
    assert '<step_output step_id="sr_cnt">' in packed
    assert "Content payload field" in packed
    assert "sr_nontext" not in packed

    # 3. Invalid dict or scalar item in step_outputs raises AppException
    for invalid_item in [{"step_id": "invalid_missing_fields"}, 12345]:
        with pytest.raises(AppException) as exc_info:
            SourceDocumentPacker.pack(
                allowed_keys={"$steps"},
                step_outputs=[invalid_item],
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


def test_source_document_packer_dotted_step_reference_and_matrix_reducer() -> None:
    """Regression test proving failure when dotted step mappings ($steps.matrix_reducer.reduced_atoms) are checked."""
    step_outputs = [
        StepOutputDTO(
            step_id="matrix_reducer",
            block_id="reduced_atoms",
            data_type="unknown",
            payload=[{"tda_id": "tda_1", "status": "FAILED"}],
        ),
        StepOutputDTO(
            step_id="sr_03c1d71000000006",
            block_id="results",
            data_type="text",
            payload={"text": "Step 6 evaluation output."},
        ),
    ]

    mappings = {
        "results": "$steps.sr_03c1d71000000006",
        "reduced_matrix": "$steps.matrix_reducer.reduced_atoms",
        "assignment_context": "$inputs.assignment_context",
    }
    allowed = SourceDocumentPacker.resolve_allowed_keys(mappings)

    # Must NOT raise AppException: Strict Fail-Fast: Mapped step(s) ['matrix_reducer.reduced_atoms'] not found in prior step outputs.
    packed = SourceDocumentPacker.pack(
        inputs_payload={"assignment_context": "The assignment brief."},
        allowed_keys=allowed,
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_03c1d71000000006">' in packed
    assert "Step 6 evaluation output." in packed
    assert "The assignment brief." in packed


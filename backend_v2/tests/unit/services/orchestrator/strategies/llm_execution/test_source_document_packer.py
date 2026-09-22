"""Unit tests for SourceDocumentPacker."""

import re
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.enums import LaxExecutionStatus
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.strategies.llm_execution.source_document_packer import (
    ContextTargetFilterDTO,
    SourceDocumentPacker,
)


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


def test_source_document_packer_step_scoping_and_context_target_filter() -> None:
    """Verify resolve_context_targets resolution and pack() key filtering according to step contracts."""
    # 1. resolve_context_targets canonical $inputs.<key> resolution
    mappings = {
        "text": "$inputs.product_text",
        "chat": "$inputs.chat_log",
        "nested": "$inputs.assignment_brief",
    }
    targets = SourceDocumentPacker.resolve_context_targets(mappings)
    assert targets.allowed_input_keys == frozenset(
        {
            "product_text",
            "chat_log",
            "assignment_brief",
        }
    )
    assert targets.allowed_step_ids is None
    assert not targets.wants_all_steps

    # 2. $steps and $steps.<step_id> mappings are resolved into step targets
    step_mappings = {
        "prior_1": "$steps.node_1",
        "prior_2": "$steps.node_2.output",
        "raw_step": "$steps",
    }
    step_targets = SourceDocumentPacker.resolve_context_targets(step_mappings)
    assert step_targets.allowed_step_ids == frozenset({"node_1", "node_2.output"})
    assert step_targets.wants_all_steps is True
    assert step_targets.allowed_input_keys is None

    # Mixed mappings
    mixed = {
        "doc": "$inputs.target_doc",
        "step": "$steps.previous",
    }
    mixed_targets = SourceDocumentPacker.resolve_context_targets(mixed)
    assert mixed_targets.allowed_input_keys == frozenset({"target_doc"})
    assert mixed_targets.allowed_step_ids == frozenset({"previous"})
    assert not mixed_targets.wants_all_steps

    # 3. Empty or None mappings yield empty sets in ContextTargetFilterDTO
    empty_targets = SourceDocumentPacker.resolve_context_targets({})
    assert empty_targets.allowed_input_keys == frozenset()
    assert empty_targets.allowed_step_ids == frozenset()
    assert not empty_targets.wants_all_steps

    none_targets = SourceDocumentPacker.resolve_context_targets(None)
    assert none_targets.allowed_input_keys == frozenset()
    assert none_targets.allowed_step_ids == frozenset()
    assert not none_targets.wants_all_steps

    # 4. pack with targets excluding unmapped inputs
    inputs = {
        "product_text": "Substantive memo text.",
        "chat_log": "Dialogue to be excluded.",
        "extra_doc": "Extra unmapped document.",
    }
    expected_inputs = [
        _build_expected_input("product_text", "Executive memo description."),
        _build_expected_input("chat_log", "Dialogue description."),
    ]
    packed = SourceDocumentPacker.pack(
        inputs,
        expected_inputs,
        targets=ContextTargetFilterDTO(allowed_input_keys=frozenset({"product_text"})),
    )
    assert "Substantive memo text." in packed
    assert '<ai_context_directive document="product_text">' in packed
    assert "Dialogue to be excluded." not in packed
    assert "chat_log" not in packed
    assert "Extra unmapped document." not in packed

    # 5. pack with empty targets returns empty string for both dict and str payloads
    assert SourceDocumentPacker.pack(inputs, expected_inputs, targets=empty_targets) == ""
    assert SourceDocumentPacker.pack("Standalone raw document", targets=empty_targets) == ""

    # Non-existent key in targets yields empty string
    non_existent_target = ContextTargetFilterDTO(allowed_input_keys=frozenset({"non_existent_key"}))
    assert SourceDocumentPacker.pack(inputs, expected_inputs, targets=non_existent_target) == ""


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
        targets=ContextTargetFilterDTO(wants_all_steps=True),
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
        targets=ContextTargetFilterDTO(allowed_step_ids=frozenset({"sr_step_1"})),
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_step_1">' in packed_single
    assert "First stage analysis summary." in packed_single
    assert '<step_output step_id="sr_step_2">' not in packed_single

    # Mixed inputs + step outputs
    inputs = {"memo": "Candidate deliverable text"}
    packed_mixed = SourceDocumentPacker.pack(
        inputs_payload=inputs,
        targets=ContextTargetFilterDTO(
            allowed_input_keys=frozenset({"memo"}),
            allowed_step_ids=frozenset({"sr_step_2"}),
        ),
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
            targets=ContextTargetFilterDTO(allowed_step_ids=frozenset({"sr_nonexistent"})),
            step_outputs=step_outputs,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name
    assert "sr_nonexistent" in exc_info.value.message


def test_source_document_packer_structured_dict_payload_and_edge_cases() -> None:
    """Test structured payload dictionary parsing, non-string mappings, and invalid items."""
    # 1. Non-string value in input_mappings
    mappings: dict[str, Any] = {"doc": "$inputs.valid", "bad": 12345}
    targets = SourceDocumentPacker.resolve_context_targets(mappings)
    assert targets.allowed_input_keys == frozenset({"valid"})

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
        targets=ContextTargetFilterDTO(wants_all_steps=True),
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
                targets=ContextTargetFilterDTO(wants_all_steps=True),
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
            payload=[
                AtomResultDTO(
                    tda_id="tda_1",
                    status=LaxExecutionStatus.PASSED,
                    evaluation_reasoning="Claim was supported.",
                    source_quote="Verbatim quote for tda_1.",
                )
            ],
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
    targets = SourceDocumentPacker.resolve_context_targets(mappings)

    # Must NOT raise AppException: Strict Fail-Fast: Mapped step(s) ['matrix_reducer.reduced_atoms'] not found in prior step outputs.
    packed = SourceDocumentPacker.pack(
        inputs_payload={"assignment_context": "The assignment brief."},
        targets=targets,
        step_outputs=step_outputs,
    )
    assert '<step_output step_id="sr_03c1d71000000006">' in packed
    assert "Step 6 evaluation output." in packed
    assert "The assignment brief." in packed


def test_source_document_packer_context_target_filter_dto_validation() -> None:
    """ISTQB Boundary: ContextTargetFilterDTO strict validation, wildcard patterns, and positive key mapping."""
    # 1. Strict validation: extra fields are forbidden
    with pytest.raises(ValidationError):
        ContextTargetFilterDTO.model_validate({"extra_field": "disallowed"})

    # 2. Direct un-prefixed input mapping resolves to allowed_input_keys
    direct_mapping = {"doc": "financials_q3"}
    targets = SourceDocumentPacker.resolve_context_targets(direct_mapping)
    assert targets.allowed_input_keys == frozenset({"financials_q3"})
    assert targets.allowed_step_ids is None

    # 3. Wildcard step mapping $steps.* sets wants_all_steps
    wildcard_mapping = {"all": "$steps.*"}
    targets_wildcard = SourceDocumentPacker.resolve_context_targets(wildcard_mapping)
    assert targets_wildcard.wants_all_steps is True
    assert targets_wildcard.allowed_step_ids is None


def test_source_document_packer_extended_coverage() -> None:
    """Test ExecutionInputsDTO, BaseModel step outputs, serialization errors, and whitespace mappings."""
    from pydantic import BaseModel, Field

    from backend_v2.core.hook_registry import ExecutionInputsDTO
    from backend_v2.exceptions import AppException
    from backend_v2.models.state import StepOutputDTO

    # 1. Whitespace and non-string mappings in resolve_context_targets
    dirty_mapping = {"empty_val": "   ", "non_str": 999}  # type: ignore[dict-item]
    empty_resolved = SourceDocumentPacker.resolve_context_targets(dirty_mapping)
    assert empty_resolved.allowed_input_keys == frozenset()
    assert empty_resolved.allowed_step_ids == frozenset()
    assert empty_resolved.wants_all_steps is False

    # 2. ExecutionInputsDTO payload in pack
    exec_inputs = ExecutionInputsDTO(
        raw_inputs={"raw_doc": "Raw document text"},
        dynamic_inputs={"dynamic_brief": "Dynamic brief text"},
    )
    packed_exec = SourceDocumentPacker.pack(inputs_payload=exec_inputs)
    assert "Raw document text" in packed_exec
    assert "Dynamic brief text" in packed_exec

    # 3. BaseModel payload in StepOutputDTO
    class DummyPayload(BaseModel):
        summary: str = Field(description="Summary")

    step_output_model = StepOutputDTO.model_construct(
        step_id="step_pydantic",
        block_id="blk_1",
        data_type="matrix",
        payload=DummyPayload(summary="Model summary content"),
    )
    packed_step = SourceDocumentPacker.pack(step_outputs=[step_output_model])
    assert '<step_output step_id="step_pydantic">' in packed_step
    assert "Model summary content" in packed_step

    # 4. JSON serialization error in StepOutputDTO payload (circular reference)
    bad_dict: dict[str, object] = {}
    bad_dict["self"] = bad_dict

    invalid_step = StepOutputDTO.model_construct(
        step_id="step_unserializable",
        block_id="blk_bad",
        data_type="matrix",
        payload=bad_dict,
    )
    with pytest.raises(AppException) as exc_info:
        SourceDocumentPacker.pack(step_outputs=[invalid_step])
    assert "Failed to serialize step payload for step step_unserializable" in str(exc_info.value)

"""Unit tests for backend_v2.services.orchestrator.strategies.llm_execution.__init__."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

import backend_v2.services.orchestrator.strategies.llm_execution as llm_execution_pkg
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.orchestrator.strategies.llm_execution import (
    ContextBuilder,
    ContextTargetFilterDTO,
    PromptFactory,
    PromptPayload,
    SourceDocumentPacker,
)


def test_llm_execution_init_public_interface_and_resolution() -> None:
    """Verify llm_execution.__init__ exports and functional target resolution."""
    expected = [
        "ContextBuilder",
        "ContextTargetFilterDTO",
        "PromptFactory",
        "PromptPayload",
        "SourceDocumentPacker",
    ]
    assert sorted(llm_execution_pkg.__all__) == expected
    assert ContextBuilder is not None
    assert PromptFactory is not None

    payload = PromptPayload(
        base_system_prompt="system",
        user_payload="user",
        atom_to_block_ids={"a0": {"blk_0195f000000070008000000000000001"}},
    )
    assert payload.base_system_prompt == "system"

    resolved = SourceDocumentPacker.resolve_context_targets(
        {"doc": "$inputs.product_text", "prior": "$steps.stp_0195f000000070008000000000000001"}
    )
    assert resolved.allowed_input_keys == frozenset({"product_text"})
    assert resolved.allowed_step_ids == frozenset({"stp_0195f000000070008000000000000001"})
    assert resolved.wants_all_steps is False


def test_negative_llm_execution_init_packer_invalid_inputs_payload_fails_fast() -> None:
    """Negative test (ISTQB): SourceDocumentPacker.pack raises AppException on invalid inputs_payload."""
    with pytest.raises(AppException) as exc_info:
        SourceDocumentPacker.pack(inputs_payload=12345)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_negative_llm_execution_init_packer_missing_mapped_step_fails_fast() -> None:
    """Negative test (ISTQB): SourceDocumentPacker.pack raises AppException when mapped step is missing."""
    targets = ContextTargetFilterDTO(
        allowed_input_keys=frozenset(),
        allowed_step_ids=frozenset({"stp_0195f000000070008000000000000099"}),
        wants_all_steps=False,
    )
    with pytest.raises(AppException) as exc_info:
        SourceDocumentPacker.pack(inputs_payload={"doc": "text"}, targets=targets, step_outputs=[])

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_negative_llm_execution_init_filter_dto_rejects_extra_fields() -> None:
    """Negative test (ISTQB): ContextTargetFilterDTO enforces extra='forbid' and strict=True."""
    with pytest.raises(ValidationError):
        ContextTargetFilterDTO.model_validate(
            {
                "allowed_input_keys": None,
                "allowed_step_ids": None,
                "wants_all_steps": False,
                "unexpected_field": "forbidden",
            }
        )

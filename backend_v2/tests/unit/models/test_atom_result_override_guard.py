import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.enums import ExecutionStatus


def test_failed_atom_rejects_override_and_quote() -> None:
    # Fail-Fast: FAILED atoms cannot have contextual_override or source_quote
    with pytest.raises(ValidationError, match="contextual_override cannot be True when status is FAILED"):
        AtomResultDTO(
            tda_id="test_id",
            status=ExecutionStatus.FAILED,
            contextual_override=True,
            source_quote="Should be stripped",
            evaluation_reasoning="Because I said so",
        )


def test_passed_atom_requires_quote_or_override() -> None:
    # Neither provided
    with pytest.raises(
        ValidationError, match="source_quote is mandatory unless contextual_override or is_inverse_evidence is True"
    ):
        AtomResultDTO(
            tda_id="test_id",
            status=ExecutionStatus.PASSED,
            contextual_override=False,
            source_quote=None,
            evaluation_reasoning="Because I said so",
        )

    # Quote provided
    dto_q = AtomResultDTO(
        tda_id="test_id",
        status=ExecutionStatus.PASSED,
        contextual_override=False,
        source_quote="Valid quote",
        evaluation_reasoning="Because I said so",
    )
    assert dto_q.source_quote == "Valid quote"
    assert dto_q.contextual_override is False

    # Override provided
    dto_o = AtomResultDTO(
        tda_id="test_id",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        source_quote=None,
        evaluation_reasoning="Because I said so",
    )
    assert dto_o.contextual_override is True


def test_passed_atom_with_override_and_quote_fails_fast() -> None:
    # Fail-Fast: source_quote must be None when contextual_override is True
    with pytest.raises(ValidationError, match="source_quote must be None when contextual_override"):
        AtomResultDTO(
            tda_id="test_id",
            status=ExecutionStatus.PASSED,
            contextual_override=True,
            source_quote="This quote should be ignored",
            evaluation_reasoning="Because I said so",
        )

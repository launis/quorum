import pytest
from pydantic import ValidationError

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import AtomResultDTO

def test_failed_atom_strips_override_and_quote() -> None:
    dto = AtomResultDTO(
        tda_id="test_id",
        status=ExecutionStatus.FAILED,
        contextual_override=True,
        source_quote="Should be stripped",
        evaluation_reasoning="Because I said so",
    )
    # The null hypothesis enforces these become False and None
    assert dto.contextual_override is False
    assert dto.source_quote is None


def test_passed_atom_requires_quote_or_override() -> None:
    # Neither provided
    with pytest.raises(ValidationError, match="source_quote is mandatory unless contextual_override is True"):
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


def test_passed_atom_with_override_and_quote_strips_quote() -> None:
    # Existing behavior: if both provided, quote is stripped
    dto = AtomResultDTO(
        tda_id="test_id",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        source_quote="This quote should be ignored",
        evaluation_reasoning="Because I said so",
    )
    assert dto.contextual_override is True
    assert dto.source_quote is None

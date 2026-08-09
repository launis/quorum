from typing import Any

from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import AtomResultDTO
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def _make_atom(
    status: ExecutionStatus = ExecutionStatus.PASSED,
    source_quote: str | None = None,
    contextual_override: bool = False,
    evaluation_reasoning: str | None = "a1 holds evidence",
) -> AtomResultDTO:
    return AtomResultDTO.model_validate(
        {
            "tda_id": "tda_123",
            "matrix_id": "mat_1",
            "status": status,
            "extracted_data": None,
            "source_quote": source_quote,
            "contextual_override": contextual_override,
            "evaluation_reasoning": evaluation_reasoning,
            "error_details": None,
            "extensions": {},
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        }
    )


def test_process_atom_evaluation_with_atom_result_dto() -> None:
    atom = _make_atom(source_quote="valid quote here")
    source_docs = [
        SourceDocumentContext(
            opaque_id="doc_1", text_content="Some long valid quote here in the text", display_name="Doc 1"
        )
    ]
    alias_map = {"a1": "doc_1"}

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=source_docs,
        mcp_source_texts=None,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quote == "valid quote here"
    assert result.evaluation_reasoning is not None
    assert "doc_1" in result.evaluation_reasoning


def test_process_atom_evaluation_contextual_override_clears_quote() -> None:
    atom_dict: dict[str, Any] = {
        "tda_id": "tda_123",
        "matrix_id": "mat_1",
        "status": ExecutionStatus.PASSED,
        "extracted_data": None,
        "source_quote": "some text",
        "contextual_override": True,
        "evaluation_reasoning": "override active",
        "error_details": None,
        "extensions": {},
        "depends_on_tda_ids": [],
        "short_circuit_reason_tda_ids": [],
    }

    atom = AtomResultDTO.model_validate(atom_dict)
    assert atom.source_quote is None

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map={},
        source_documents=[],
    )
    assert result.source_quote is None


def test_process_atom_evaluation_no_match_preserves_quote() -> None:
    atom = _make_atom(source_quote="unmatched quote")
    source_docs = [
        SourceDocumentContext(opaque_id="doc_1", text_content="Completely different text", display_name="Doc 1")
    ]
    alias_map = {"a1": "doc_1"}

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=source_docs,
        mcp_source_texts=None,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quote == "unmatched quote"


def test_process_atom_evaluation_mcp_source_match() -> None:
    atom = _make_atom(source_quote="mcp matching quote")
    alias_map = {"a1": "doc_1"}
    mcp_texts = {"a1": "Here is the mcp matching quote for the test"}

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=[],
        mcp_source_texts=mcp_texts,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quote == "mcp matching quote"


def test_process_atom_evaluation_none_source_quote_skips_matching() -> None:
    atom = _make_atom(source_quote=None, contextual_override=True, evaluation_reasoning="a1 reason")

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom, alias_map={"a1": "doc_1"}, source_documents=[], mcp_source_texts=None
    )

    assert result.source_quote is None
    assert result.evaluation_reasoning is not None
    assert "doc_1" in result.evaluation_reasoning

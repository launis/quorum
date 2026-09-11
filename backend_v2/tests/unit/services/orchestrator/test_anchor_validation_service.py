from unittest.mock import patch

import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import ExecutionStatus, TargetSpeaker
from backend_v2.models.v2_core import AtomResultDTO
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_anchor_validation_exact_match() -> None:
    pdf_text = "This is a simple test document. It contains some text."
    exact_quotes = ["simple test document"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "simple test document"


def test_anchor_validation_encoding_resilience() -> None:
    # Simulate a corrupted source text where 'ä' and 'ö' were lost, leaving 'tst'
    pdf_text = "Johtoryhma paatti etta tee t\ufffdt\ufffd muistio tasta kokouksesta."

    # Simulate the LLM outputting the correct, inferred spelling
    exact_quotes = ["tee tästä muistio"]

    # This should pass fuzzy matching since '\ufffd' is mapped to 'a' and 'ä' is mapped to 'a'
    # norm_quote: teetastamuistio
    # norm_pdf: ...teetatamustio... -> teetastamuistio matches teetatamuistio (92.8%) > 80%
    extracted = AnchorValidationService.validate_evidence(
        pdf_text=pdf_text,
        exact_quotes=exact_quotes,
        locale="fi",
        strictness_level=50,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == exact_quotes[0]  # Returns the LLM quote due to fuzzy match fallback


def test_anchor_validation_html_tags_ignored() -> None:
    pdf_text = "Tee <b>tästä</b> muistio"
    exact_quotes = ["Tee tästä muistio"]

    # The HTML tags are dropped from normalization
    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Tee <b>tästä</b> muistio"


def test_anchor_validation_trace_contradiction() -> None:
    with pytest.raises(SemanticEvidenceError, match="Logical contradiction"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[5. validation decision: fail]"
        )


def test_anchor_validation_hallucinated_anchor() -> None:
    with pytest.raises(SemanticEvidenceError, match="Hallucinated Anchor"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[2. SYNTACTIC ANCHOR: 'hallucination']"
        )


def test_anchor_validation_provenance_violation() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes)


def test_anchor_validation_provenance_user_rejects_ai_text() -> None:
    """Cross-speaker rejection: USER claim quoting AI text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_ai_rejects_user_text() -> None:
    """Cross-speaker rejection (SYMMETRIC - Amendment 3): AI claim quoting user text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)


def test_anchor_validation_provenance_success() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_user_accepts_user_text() -> None:
    """Valid quote acceptance: USER claim quoting user text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_ai_accepts_ai_text() -> None:
    """Valid quote acceptance: AI claim quoting AI text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Some AI generated text about cats"


def test_anchor_validation_non_chat_document_user_claim_passes() -> None:
    """Non-chat document: USER claim quoting full document text without dialogue tags passes."""
    pdf_text = "Tämä on yksittäisen kirjoittajan strateginen muistio ilman dialogia."
    exact_quotes = ["strateginen muistio"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "strateginen muistio"



def test_anchor_validation_empty_inputs() -> None:
    assert AnchorValidationService.normalize_text_with_mapping("") == ("", [])
    assert AnchorValidationService.strict_match("", ["quote"]) is False
    assert AnchorValidationService.strict_match("text", []) is False
    assert AnchorValidationService.strict_match("text", [""]) is False

    with pytest.raises(SemanticEvidenceError, match="exact_quotes is required"):
        AnchorValidationService.validate_evidence("text", [])


def test_anchor_validation_contextual_override() -> None:
    assert AnchorValidationService.validate_evidence("text", [], contextual_override=True) is None


def test_anchor_validation_too_long_quote() -> None:
    with pytest.raises(SemanticEvidenceError, match="Quote length exceeds safety limit"):
        AnchorValidationService.validate_evidence("text", ["A" * 1001])


def test_anchor_validation_empty_anchor_ban() -> None:
    with pytest.raises(SemanticEvidenceError, match="Cannot pass validation without a physical syntactic anchor"):
        AnchorValidationService.validate_evidence("text", ["text"], reasoning_trace="[2. syntactic anchor: none]")


def test_anchor_validation_entropy_gate_failure() -> None:
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        # length < 10 and not an exact match
        AnchorValidationService.validate_evidence("some other text", ["short"])


def test_anchor_validation_absolute_strictness() -> None:
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.get_lexical_fuzz_threshold", return_value=100.0
    ):
        with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
            # strictness 100 forces threshold > 100 (which is capped at 100) and requires 100% exact match
            AnchorValidationService.validate_evidence(
                "almost perfect text", ["almost perfect texxxt"], strictness_level=100
            )


def test_anchor_validation_coverage_fallback() -> None:
    # Fuzzy score < 80% but coverage > 50%
    # norm_quote = "the quick brown fox jumps"
    # norm_text = "the quick brown fox"
    # Fuzzy score will be low because quote is longer than text.
    extracted = AnchorValidationService.validate_evidence(
        "the quick brown fox", ["the quick brown fox jumps"], strictness_level=0
    )
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "the quick brown fox jumps"


def test_anchor_validation_strictness_multiplier() -> None:
    # Testing strictness 85 and 30 paths
    # Just need to hit the lines in _is_lexically_valid
    with pytest.raises(SemanticEvidenceError):
        AnchorValidationService.validate_evidence("some text", ["completely different text"], strictness_level=85)

    with pytest.raises(SemanticEvidenceError):
        AnchorValidationService.validate_evidence("some text", ["completely different text"], strictness_level=30)


def test_anchor_validation_no_tags_fallback() -> None:
    pdf_text = "This is a normal document without XML tags."
    exact_quotes = ["normal document"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "normal document"


def test_anchor_validation_strict_match() -> None:
    assert AnchorValidationService.strict_match("hello world document text", ["hello world"]) is True
    assert AnchorValidationService.strict_match("hello world document text", ["absent quote"]) is False
    assert AnchorValidationService.strict_match("hello world document text", [""]) is False


def test_anchor_validation_calculate_fuzzy_score_long_quote() -> None:
    long_quote = "this is a very long normalized quote with more than thirty chars"
    source = "this is a very long normalized quote with more than thirty characters in it"
    score = AnchorValidationService.calculate_fuzzy_score(long_quote, source)
    assert score > 80.0


def test_anchor_validation_quote_normalized_to_empty_string_fails() -> None:
    pdf_text = "Standard valid document text."
    with pytest.raises(SemanticEvidenceError, match="normalized to empty string"):
        AnchorValidationService.validate_evidence(pdf_text, ["???"])


def test_anchor_validation_provenance_empty_allowed_stream_fails() -> None:
    # Only <ai_draft_context> present, but claim targets USER
    pdf_text = "<ai_draft_context>Model output here.</ai_draft_context>"
    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(
            pdf_text, ["Model output"], target_speaker=TargetSpeaker.USER
        )


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
    atom = AtomResultDTO.model_validate(
        {
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
    )
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


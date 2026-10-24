"""Unit tests for the AnchorValidationService package facade and QGR017 guardrail lockdown."""

from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import ExecutionStatus, TargetSpeaker
from backend_v2.services.orchestrator.anchor_validation import (
    MAX_CITATION_SPAN_CHARS,
    MIN_ENTROPY_GATE_CHARS,
    MIN_MULTI_SEGMENT_FLOOR_CHARS,
    AnchorValidationService,
    calculate_fuzzy_score,
    is_lexically_valid,
    normalize_text_with_mapping,
    process_atom_evaluation,
    strict_match,
    validate_evidence,
)
from scripts._ast_guardrails import GuardrailSeverity, scan_source_code_for_guardrails


def test_anchor_validation_facade_full_parity() -> None:
    """Contract test: Verify AnchorValidationService facade preserves 100% parity across all 6 static methods."""
    assert AnchorValidationService.MAX_CITATION_SPAN_CHARS == MAX_CITATION_SPAN_CHARS == 1000
    assert AnchorValidationService.MIN_MULTI_SEGMENT_FLOOR_CHARS == MIN_MULTI_SEGMENT_FLOOR_CHARS == 30
    assert AnchorValidationService.MIN_ENTROPY_GATE_CHARS == MIN_ENTROPY_GATE_CHARS == 10

    sample_text = "Strateginen johtaminen edellyttää selkeitä tavoitteita ja seurantaa."
    sample_quote = "selkeitä tavoitteita"

    # 1. normalize_text_with_mapping
    facade_norm = AnchorValidationService.normalize_text_with_mapping(sample_text)
    direct_norm = normalize_text_with_mapping(sample_text)
    assert facade_norm == direct_norm

    # 2. strict_match
    facade_strict = AnchorValidationService.strict_match(sample_text, [sample_quote])
    direct_strict = strict_match(sample_text, [sample_quote])
    assert facade_strict == direct_strict
    assert facade_strict.is_valid is True

    # 3. calculate_fuzzy_score
    norm_q, _ = facade_norm[0], facade_norm[1]
    facade_fuzzy = AnchorValidationService.calculate_fuzzy_score(norm_q, facade_norm[0])
    direct_fuzzy = calculate_fuzzy_score(norm_q, direct_norm[0])
    assert facade_fuzzy == direct_fuzzy == 100.0

    # 4. _is_lexically_valid
    norm_quote_str, _ = AnchorValidationService.normalize_text_with_mapping(sample_quote)
    facade_lex = AnchorValidationService._is_lexically_valid(
        quote=sample_quote,
        norm_quote=norm_quote_str,
        norm_text=facade_norm[0],
        strictness_level=50,
        locale="fi",
        source_text=sample_text,
        lexical_strictness_level=50,
    )
    direct_lex = is_lexically_valid(
        quote=sample_quote,
        norm_quote=norm_quote_str,
        norm_text=direct_norm[0],
        strictness_level=50,
        locale="fi",
        source_text=sample_text,
        lexical_strictness_level=50,
    )
    assert facade_lex == direct_lex
    assert facade_lex.is_valid is True

    # 5. validate_evidence
    facade_ev = AnchorValidationService.validate_evidence(
        pdf_text=sample_text,
        exact_quotes=[sample_quote],
        locale="fi",
        strictness_level=50,
        target_speaker=TargetSpeaker.USER,
        lexical_strictness_level=50,
    )
    direct_ev = validate_evidence(
        pdf_text=sample_text,
        exact_quotes=[sample_quote],
        locale="fi",
        strictness_level=50,
        target_speaker=TargetSpeaker.USER,
        lexical_strictness_level=50,
    )
    assert facade_ev == direct_ev == ("selkeitä tavoitteita",)

    # 6. process_atom_evaluation
    atom = AtomResultDTO(
        tda_id="tda_123",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(sample_quote,),
        contextual_override=False,
        evaluation_reasoning="a1 contains evidence",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    docs = [SourceDocumentContext(opaque_id="doc_1", text_content=sample_text, display_name="Doc 1")]
    facade_atom = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map={"a1": "doc_1"},
        source_documents=docs,
        mcp_source_texts=None,
        locale="fi",
        strictness_level=50,
        lexical_strictness_level=50,
    )
    direct_atom = process_atom_evaluation(
        atom=atom,
        alias_map={"a1": "doc_1"},
        source_documents=docs,
        mcp_source_texts=None,
        locale="fi",
        strictness_level=50,
        lexical_strictness_level=50,
    )
    assert facade_atom == direct_atom
    assert facade_atom.evaluation_reasoning == "doc_1 contains evidence"


def test_qgr017_bans_legacy_anchor_validation_service_import() -> None:
    """Contract test: Verify QGR017 flags any import from backend_v2.services.orchestrator.anchor_validation_service."""
    snippets = [
        "import backend_v2.services.orchestrator.anchor_validation_service\n",
        "from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService\n",
        "from backend_v2.services.orchestrator import anchor_validation_service\n",
    ]
    for code in snippets:
        violations = scan_source_code_for_guardrails("backend_v2/services/sample.py", code.encode("utf-8"))
        qgr017_violations = [v for v in violations if v.rule_code == "QGR017"]
        assert len(qgr017_violations) == 1
        assert qgr017_violations[0].severity == GuardrailSeverity.FATAL
        assert "backend_v2.services.orchestrator.anchor_validation" in qgr017_violations[0].remediation

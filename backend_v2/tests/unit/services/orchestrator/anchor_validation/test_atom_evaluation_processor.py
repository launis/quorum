"""Unit tests for atom_evaluation_processor.py (process_atom_evaluation across AtomResultDTO)."""

from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.anchor_validation.atom_evaluation_processor import (
    process_atom_evaluation,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import strict_match


def _make_atom(
    status: ExecutionStatus = ExecutionStatus.PASSED,
    source_quotes: tuple[str, ...] | list[str] | str | None = None,
    contextual_override: bool = False,
    evaluation_reasoning: str | None = "a1 holds evidence",
) -> AtomResultDTO:
    return AtomResultDTO(
        tda_id="tda_123",
        matrix_id="mat_1",
        status=status,
        extracted_data=None,
        source_quotes=source_quotes,
        contextual_override=contextual_override,
        evaluation_reasoning=evaluation_reasoning,
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )


def test_process_atom_evaluation_with_atom_result_dto() -> None:
    atom = _make_atom(source_quotes=("valid quote here",))
    source_docs = [
        SourceDocumentContext(
            opaque_id="doc_1", text_content="Some long valid quote here in the text", display_name="Doc 1"
        )
    ]
    alias_map = {"a1": "doc_1"}

    result = process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=source_docs,
        mcp_source_texts=None,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quotes == ("valid quote here",)
    assert result.evaluation_reasoning is not None
    assert "doc_1" in result.evaluation_reasoning


def test_process_atom_evaluation_with_inflected_quote_matching() -> None:
    atom = _make_atom(source_quotes=("johtajuus ja selkeät tavoitteet",))
    source_docs = [
        SourceDocumentContext(
            opaque_id="doc_1",
            text_content="Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan.",
            display_name="Doc 1",
        )
    ]
    alias_map = {"a1": "doc_1"}

    result = process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=source_docs,
        mcp_source_texts=None,
        locale="fi",
        strictness_level=50,
    )

    assert result.source_quotes == ("johtajuus ja selkeät tavoitteet",)
    assert result.evaluation_reasoning is not None
    assert "doc_1" in result.evaluation_reasoning


def test_process_atom_evaluation_contextual_override_clears_quote() -> None:
    atom = AtomResultDTO(
        tda_id="tda_123",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=None,
        contextual_override=True,
        evaluation_reasoning="override active",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    assert atom.source_quotes is None

    result = process_atom_evaluation(
        atom=atom,
        alias_map={},
        source_documents=[],
    )
    assert result.source_quotes is None


def test_process_atom_evaluation_no_match_preserves_quote() -> None:
    atom = _make_atom(source_quotes=("unmatched quote",))
    source_docs = [
        SourceDocumentContext(opaque_id="doc_1", text_content="Completely different text", display_name="Doc 1")
    ]
    alias_map = {"a1": "doc_1"}

    result = process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=source_docs,
        mcp_source_texts=None,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quotes == ("unmatched quote",)


def test_process_atom_evaluation_mcp_source_match() -> None:
    atom = _make_atom(source_quotes=("mcp matching quote",))
    alias_map = {"a1": "doc_1"}
    mcp_texts = {"a1": "Here is the mcp matching quote for the test"}

    result = process_atom_evaluation(
        atom=atom,
        alias_map=alias_map,
        source_documents=[],
        mcp_source_texts=mcp_texts,
        locale="en",
        strictness_level=100,
    )

    assert result.source_quotes == ("mcp matching quote",)


def test_process_atom_evaluation_none_source_quote_skips_matching() -> None:
    atom = _make_atom(source_quotes=None, contextual_override=True, evaluation_reasoning="a1 reason")

    result = process_atom_evaluation(
        atom=atom, alias_map={"a1": "doc_1"}, source_documents=[], mcp_source_texts=None
    )

    assert result.source_quotes is None
    assert result.evaluation_reasoning is not None
    assert "doc_1" in result.evaluation_reasoning


def test_anchor_validation_process_atom_evaluation_suite() -> None:
    """Verifies that process_atom_evaluation suite runs end-to-end."""
    test_process_atom_evaluation_with_atom_result_dto()
    test_process_atom_evaluation_with_inflected_quote_matching()
    test_process_atom_evaluation_contextual_override_clears_quote()
    test_process_atom_evaluation_no_match_preserves_quote()
    test_process_atom_evaluation_mcp_source_match()
    test_process_atom_evaluation_none_source_quote_skips_matching()


def test_anchor_validation_process_atom_evaluation_cross_document_chimera_fails() -> None:
    """Negative ISTQB test: cross-document chimera across separate SourceDocumentContext instances fails matching."""
    doc1 = SourceDocumentContext(
        opaque_id="doc_1",
        text_content="Dokumentti yksi sisältää tämän ensimmäisen lauseen tässä.",
        display_name="Doc 1",
    )
    doc2 = SourceDocumentContext(
        opaque_id="doc_2",
        text_content="Dokumentti kaksi sisältää tämän toisen lauseen erikseen.",
        display_name="Doc 2",
    )
    seg1 = "Dokumentti yksi sisältää tämän ensimmäisen lauseen tässä."
    seg2 = "Dokumentti kaksi sisältää tämän toisen lauseen erikseen."

    atom = AtomResultDTO(
        tda_id="tda_123",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(seg1, seg2),
        contextual_override=False,
        evaluation_reasoning="a1 points to evidence across documents",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    result = process_atom_evaluation(
        atom=atom,
        alias_map={"a1": "doc_1"},
        source_documents=[doc1, doc2],
        mcp_source_texts=None,
        locale="fi",
        strictness_level=100,
    )
    assert result.source_quotes == (seg1, seg2)
    assert strict_match(doc1.text_content, (seg1, seg2)).is_valid is False
    assert strict_match(doc2.text_content, (seg1, seg2)).is_valid is False


def test_anchor_validation_process_atom_evaluation_mcp_and_fuzzy_branches() -> None:
    """Tests process_atom_evaluation with MCP texts and fuzzy matching branches."""
    seg1 = "Tämä on ensimmäinen lause MCP dokumentissa riittävän pitkänä."
    seg2 = "Tämä on toinen lause MCP dokumentissa riittävän pitkänä."
    atom = AtomResultDTO(
        tda_id="tda_mcp",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(seg1, seg2),
        contextual_override=False,
        evaluation_reasoning="Evidence found in dynamic MCP tool output",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    mcp_text = f"Alkutekstiä. {seg1} Väliosa tähän. {seg2} Lopputekstiä."
    res_mcp = process_atom_evaluation(
        atom=atom,
        alias_map={},
        source_documents=[],
        mcp_source_texts={"tool_1": mcp_text},
        locale="fi",
        strictness_level=100,
    )
    assert res_mcp.source_quotes is not None
    assert len(res_mcp.source_quotes) == 2

    fuzzy_seg1 = "Organisaation strateginen kehityssuunnitelma määrittelee tulevat tavoitteet selkeästi."
    fuzzy_seg2 = "Toiminnan tuloksellisuutta seurataan säännöllisesti ja systemaattisesti koko organisaatiossa."
    doc = SourceDocumentContext(
        opaque_id="doc_fuzzy",
        text_content=f"{fuzzy_seg1} Väliosa. {fuzzy_seg2}",
        display_name="Fuzzy Doc",
    )
    atom_fuzzy = AtomResultDTO(
        tda_id="tda_fuz",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(
            "Organisaation strateginen kehityssuunnidelma määrittelee tulevat tavoitteet selkeästi.",
            "Toiminnan tuloksellisuutta seurataan säännollisesti ja systemaattisesti koko organisaatiossa.",
        ),
        contextual_override=False,
        evaluation_reasoning="Fuzzy evidence matching",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    res_fuzzy = process_atom_evaluation(
        atom=atom_fuzzy,
        alias_map={},
        source_documents=[doc],
        mcp_source_texts=None,
        locale="fi",
        strictness_level=50,
    )
    assert res_fuzzy.source_quotes is not None

    res_mcp_fuzzy = process_atom_evaluation(
        atom=atom_fuzzy,
        alias_map={},
        source_documents=[],
        mcp_source_texts={"mcp_tool": doc.text_content},
        locale="fi",
        strictness_level=50,
    )
    assert res_mcp_fuzzy.source_quotes is not None

    # Unmatched fuzzy in both static doc and MCP text
    unmatched_doc = SourceDocumentContext(
        opaque_id="doc_unmatched",
        text_content="Täysin eri tekstiä joka ei vastaa lainkaan haettuja lauseita.",
        display_name="Unmatched Doc",
    )
    res_unmatched = process_atom_evaluation(
        atom=atom_fuzzy,
        alias_map={},
        source_documents=[unmatched_doc],
        mcp_source_texts={"mcp_tool": "Täysin eri MCP tekstiä joka ei vastaa lainkaan."},
        locale="fi",
        strictness_level=50,
    )
    assert res_unmatched.source_quotes == atom_fuzzy.source_quotes

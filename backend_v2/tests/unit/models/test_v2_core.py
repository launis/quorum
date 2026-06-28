from backend_v2.models.v2_core import ReportDataDTO

# Import existing tests so they are included in the coverage run for v2_core.py
from backend_v2.tests.unit.test_v2_core_models import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_strictness import *  # noqa: F403, F401


def test_report_data_dto_strictness_level_validation() -> None:
    dto = ReportDataDTO.model_validate(
        {
            "workflow_id": "wf_1",
            "profile_id": "prof_1",
        }
    )
    assert dto.strictness_level is None


def test_evidence_quote_dto_id_generation() -> None:
    from backend_v2.models.v2_core import EvidenceQuoteDTO

    quote1 = EvidenceQuoteDTO(text="Test quote 1")
    quote2 = EvidenceQuoteDTO(text="Test quote 2")

    assert quote1.id.startswith("evq_")
    assert quote2.id.startswith("evq_")
    assert len(quote1.id) == 36
    assert quote1.id != quote2.id

    # Test None sanitization
    quote3 = EvidenceQuoteDTO(text="Test quote 3", used_evidence_ids=None)
    assert quote3.used_evidence_ids == []


def test_row_forensics_dto_all_evidence_rejected() -> None:
    from backend_v2.models.v2_core import EvidenceQuoteDTO, LevelQuotesDTO, RowForensicsDTO

    # Empty Row
    row_empty = RowForensicsDTO(level_quotes=[])
    assert row_empty.all_evidence_rejected is False

    # All quotes rejected
    q1 = EvidenceQuoteDTO(text="Quote 1", user_rejected=True)
    q2 = EvidenceQuoteDTO(text="Quote 2", user_rejected=True)
    level_all_rejected = LevelQuotesDTO(level=1, level_name="L1", quotes=[q1, q2])
    row_all_rejected = RowForensicsDTO(level_quotes=[level_all_rejected])
    assert row_all_rejected.all_evidence_rejected is True

    # Mixed quotes rejected
    q3 = EvidenceQuoteDTO(text="Quote 3", user_rejected=False)
    level_mixed = LevelQuotesDTO(level=2, level_name="L2", quotes=[q1, q3])
    row_mixed = RowForensicsDTO(level_quotes=[level_mixed])
    assert row_mixed.all_evidence_rejected is False


def test_mcp_audit_trace_new_fields() -> None:
    from backend_v2.models.v2_core import MCPAuditTrace

    trace = MCPAuditTrace(
        tool_id="test_tool",
        step_name="test_step",
        query="test query",
        knowledge_gap="What is the test about?",
        search_rationale="To verify the test.",
        reasoning="Because it is a test.",
    )
    assert trace.knowledge_gap == "What is the test about?"
    assert trace.search_rationale == "To verify the test."


def test_citation_extraction_item_dto_new_fields() -> None:
    from backend_v2.models.domain.mcp import CitationExtractionItemDTO

    item = CitationExtractionItemDTO(
        claim_text="This is a claim",
        search_query="Search query",
        knowledge_gap="Need more info",
        search_rationale="To be certain",
        reasoning="Just in case",
    )
    assert item.knowledge_gap == "Need more info"
    assert item.search_rationale == "To be certain"

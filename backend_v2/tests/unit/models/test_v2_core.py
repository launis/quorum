from unittest.mock import AsyncMock
from backend_v2.models.v2_core import ReportDataDTO

# Import existing tests so they are included in the coverage run for v2_core.py
from backend_v2.tests.unit.test_v2_core_models import *  # noqa: F403, F401
from backend_v2.tests.unit.test_v2_core_strictness import *  # noqa: F403, F401


def test_report_data_dto_strictness_level_validation() -> None:
    dto = ReportDataDTO.model_validate(
        {
            "workflow_id": "wf_1",
            "execution_id": "exe_1",
            "profile_id": "prof_1",
        }
    )
    assert dto.strictness_level is None


def test_scorecard_atom_dto_firewall() -> None:
    from backend_v2.models.enums import ExecutionStatus, VisualIntent
    from backend_v2.models.v2_core import ScorecardAtomDTO

    larger_payload = {
        "atom_id": "atom_1",
        "level": 1,
        "level_name": "Level 1",
        "claim_label": "Claim 1",
        "extracted_facts": {},
        "exact_quotes": [{"quote": "Quote 1", "source_alias": "DOC-1"}],
        "internal_logic_en": {
            "step_1_identify_premise": "1",
            "step_2_scan_source": "2",
            "step_3_evaluate_anti_patterns": "3",
            "step_4_final_conclusion": "4",
        },
        "status": ExecutionStatus.PASSED,
        "semantic_reasoning": "Reason",
        "contextual_override": False,
        "structural_location": "N/A",
        "chart_display_label": "N/A",
        "visual_intent": VisualIntent.NEUTRAL,
        "db_secret_key": "should_be_stripped",
        "internal_ai_score": 0.99,
    }

    dto = ScorecardAtomDTO.model_validate(larger_payload, context={"alias_registry": {"DOC-1": "opaque_1"}})

    assert dto.atom_id == "atom_1"
    assert not hasattr(dto, "db_secret_key")
    assert not hasattr(dto, "internal_ai_score")


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

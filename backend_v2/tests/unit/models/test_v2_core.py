import pytest
from pydantic import ValidationError

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
        "exact_quotes": [{"quote": "Quote 1", "source_id": "DOC-1"}],
        "internal_logic_en": {
            "step_1_identify_premise": "1",
            "step_2_scan_source": "2",
            "step_3_evaluate_anti_patterns": "3",
            "step_4_final_conclusion": "4",
        },
        "status": ExecutionStatus.PASSED,
        "semantic_reasoning": "Reason",
        "contextual_override": False,
        "structural_location": None,
        "chart_display_label": "N/A",
        "visual_intent": VisualIntent.NEUTRAL,
        "db_secret_key": "should_be_stripped",
        "internal_ai_score": 0.99,
    }

    with pytest.raises(ValidationError):
        ScorecardAtomDTO.model_validate(larger_payload, context={"alias_registry": {"DOC-1": "opaque_1"}})


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


def test_report_data_dto_rejects_legacy_fields() -> None:
    from backend_v2.models.v2_core import ReportDataDTO

    # Test 1: evaluative_matrices is forbidden
    with pytest.raises(ValidationError) as exc_info:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "evaluative_matrices": []}
        )
    assert "evaluative_matrices" in str(exc_info.value)

    # Test 2: content_blocks is forbidden
    with pytest.raises(ValidationError) as exc_info2:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "content_blocks": []}
        )
    assert "content_blocks" in str(exc_info2.value)

    # Test 3: penalties_applied is forbidden
    with pytest.raises(ValidationError) as exc_info3:
        ReportDataDTO.model_validate(
            {"workflow_id": "wf_1", "execution_id": "exe_1", "profile_id": "prof_1", "penalties_applied": []}
        )
    assert "penalties_applied" in str(exc_info3.value)


def test_scorecard_atom_contested_warning_mapping() -> None:
    from backend_v2.models.enums import ExecutionStatus, VisualIntent
    from backend_v2.models.v2_core import ScorecardAtomDTO

    payload = {
        "atom_id": "atom_1",
        "level": 1,
        "level_name": "Level 1",
        "claim_label": "Claim 1",
        "extracted_facts": {},
        "exact_quotes": [],
        "internal_logic_en": {
            "step_1_identify_premise": "1",
            "step_2_scan_source": "2",
            "step_3_evaluate_anti_patterns": "3",
            "step_4_final_conclusion": "4",
        },
        "status": ExecutionStatus.PASSED,
        "semantic_reasoning": "Reason",
        "contextual_override": True,
        "structural_location": None,
        "chart_display_label": "N/A",
        "visual_intent": VisualIntent.NEUTRAL,
    }

    dto = ScorecardAtomDTO.model_validate(payload)
    assert dto.visual_intent == VisualIntent.WARNING

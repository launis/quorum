import pytest

from backend_v2.models.v2_core import ReasoningStepDTO, ScorecardAtomDTO


def test_scorecard_atom_dto_has_epic90_fields():
    """Tier 4 TDD Repro: Verify ScorecardAtomDTO supports chart_display_label and visual_intent."""
    # We simulate passing the fields that the UI expects
    try:
        dto = ScorecardAtomDTO(
            atom_id="atm_123",
            level=1,
            level_name="Level 1",
            claim_label="Test",
            extracted_facts={},
            exact_quotes=[],
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="a",
                step_2_scan_source="b",
                step_3_evaluate_anti_patterns="c",
                step_4_final_conclusion="d",
            ),
            status="PASS",
            semantic_reasoning="reason",
            contextual_override=False,
            structural_location="loc",
            chart_display_label="Short Label",
            visual_intent="NEUTRAL",
        )
    except Exception as e:
        pytest.fail(f"ScorecardAtomDTO failed to instantiate with Epic 90 fields: {e}")

    # Verify the fields are accessible and dumped correctly
    dumped = dto.model_dump()
    assert "chart_display_label" in dumped, "Missing chart_display_label in serialization output"
    assert "visual_intent" in dumped, "Missing visual_intent in serialization output"

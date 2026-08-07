from backend_v2.models.dtos.atom_evaluation import (
    AtomEvaluationItemDTO,
    ReasoningStepDTO,
)


def test_atom_evaluation_item_dto_contested_state() -> None:
    """Test that CONTESTED status bypasses inverse_evidence logic."""
    item = AtomEvaluationItemDTO(
        chart_display_label="TestLabel",
        visual_intent="info",
        atom_id="atom_contested",
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="stub",
            step_2_scan_source="stub",
            step_3_evaluate_anti_patterns="stub",
            step_4_final_conclusion="stub",
        ),
        extracted_facts={"fact_1": "Found"},
        status="CONTESTED",
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location=None,
    )
    # Phase 1: CONTESTED bypasses inversion logic
    assert item.calculate_rule_satisfied(inverse_evidence=False) is True
    assert item.calculate_rule_satisfied(inverse_evidence=True) is True

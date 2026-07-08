import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import AtomEvaluationItemDTO


def test_atom_evaluation_item_truncates_chart_label():
    base_data = {
        "atom_id": "test",
        "semantic_reasoning": "Reasoning " * 10,
        "contextual_override": False,
        "structural_location": "N/A",
        "internal_logic_en": {
            "step_1_identify_premise": "a",
            "step_2_scan_source": "b",
            "step_3_evaluate_anti_patterns": "c",
            "step_4_final_conclusion": "d",
        },
        "visual_intent": "success",
    }

    # Case 1: Less than 3 words, under 25 chars -> unchanged
    data = base_data.copy()
    data["chart_display_label"] = "Short label"
    dto = AtomEvaluationItemDTO.model_validate(data)
    assert dto.chart_display_label == "Short label"

    # Case 2: > 3 words, under 25 chars -> truncated words
    data["chart_display_label"] = "One two three four"
    dto = AtomEvaluationItemDTO.model_validate(data)
    assert dto.chart_display_label == "One two three..."

    # Case 3: 3 words, > 25 chars -> truncated length
    data["chart_display_label"] = "VeryLongWord1 VeryLongWord2 VeryLongWord3"
    dto = AtomEvaluationItemDTO.model_validate(data)
    assert len(dto.chart_display_label) == 25
    assert dto.chart_display_label.endswith("...")

    # Case 4: > 3 words and combined length > 25 chars -> truncated words and length
    data["chart_display_label"] = "ThisIsALongWord And Another Long Word"
    dto = AtomEvaluationItemDTO.model_validate(data)
    assert dto.chart_display_label == "ThisIsALongWord And An..."
    assert len(dto.chart_display_label) <= 25


def test_atom_evaluation_item_rejects_invalid_visual_intent():
    base_data = {
        "atom_id": "test",
        "chart_display_label": "Label",
        "semantic_reasoning": "Reasoning " * 10,
        "contextual_override": False,
        "structural_location": "N/A",
        "internal_logic_en": {
            "step_1_identify_premise": "a",
            "step_2_scan_source": "b",
            "step_3_evaluate_anti_patterns": "c",
            "step_4_final_conclusion": "d",
        },
    }

    # valid
    for intent in ["success", "warning", "critical_override", "info"]:
        d = base_data.copy()
        d["visual_intent"] = intent
        dto = AtomEvaluationItemDTO.model_validate(d)
        assert dto.visual_intent == intent

    # invalid
    d = base_data.copy()
    d["visual_intent"] = "invalid_intent"
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(d)

    # missing (should fail since it's required with no default)
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(base_data)

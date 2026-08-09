from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_evaluation import (
    AtomEvaluationItemDTO,
    LightweightExtractionAtom,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput


def _make_atom_raw(status: str | None = None) -> dict[str, Any]:
    return {
        "atom_id": "1",
        "used_source_aliases": [],
        "used_evidence_ids": [],
        "extracted_facts": {"fact": "valid"},
        "exact_quotes": [{"text": "valid", "original_language_text": "valid", "source_id": "doc1"}],
        "internal_logic_en": {
            "step_1_identify_premise": "",
            "step_2_scan_source": "",
            "step_3_evaluate_anti_patterns": "",
            "step_4_final_conclusion": "",
        },
        "chart_display_label": "lbl",
        "visual_intent": "info",
        "semantic_reasoning": "reason",
        "contextual_override": False,
        "structural_location": None,
        "status": status,
        "counter_quote": None,
    }


_ctx: dict[str, Any] = {"alias_map": {}, "mcp_source_texts": {}}


def test_atom_evaluation_item_dto_evidence_found() -> None:
    raw_bad = _make_atom_raw()
    raw_bad["confidence"] = 2.0
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(raw_bad, context=_ctx)

    raw_null = _make_atom_raw()
    raw_null["extracted_facts"] = {"fact": "null"}
    raw_null["exact_quotes"] = [{"text": "null", "original_language_text": "null", "source_id": "1"}]
    item1 = AtomEvaluationItemDTO.model_validate(raw_null, context=_ctx)
    assert not item1.evidence_found

    item2 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(), context=_ctx)
    assert item2.evidence_found


def test_atom_evaluation_item_dto_calculate_rule_satisfied() -> None:
    item = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status="DLQ"), context=_ctx)
    assert item.calculate_rule_satisfied(inverse_evidence=False) == "DLQ"

    item2 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status="CONTESTED"), context=_ctx)
    assert item2.calculate_rule_satisfied(inverse_evidence=False) is True

    item3 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status="PASS"), context=_ctx)
    assert item3.calculate_rule_satisfied(inverse_evidence=True) is False
    assert item3.calculate_rule_satisfied(inverse_evidence=False) is True

    item4 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status=None), context=_ctx)
    assert item4.calculate_rule_satisfied(inverse_evidence=True) is False
    assert item4.calculate_rule_satisfied(inverse_evidence=False) is True

    item5 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status="FAIL"), context=_ctx)
    assert item5.calculate_rule_satisfied(inverse_evidence=True) is True
    assert item5.calculate_rule_satisfied(inverse_evidence=False) is False

    item6 = AtomEvaluationItemDTO.model_validate(_make_atom_raw(status=None), context=_ctx)
    assert item6.calculate_rule_satisfied(inverse_evidence=False, allow_contextual_override=True) is True


def test_atom_evaluation_item_dto_context_override() -> None:
    raw = _make_atom_raw()
    raw["semantic_reasoning"] = "short"
    raw["contextual_override"] = True
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(raw, context=_ctx)

    raw2 = _make_atom_raw()
    raw2["semantic_reasoning"] = "A" * 55
    raw2["contextual_override"] = True
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(raw2, context=_ctx)


def test_atom_evaluation_item_dto_truncate_label() -> None:
    raw = _make_atom_raw()
    raw["chart_display_label"] = "This is a very long label that goes over 25 characters and many words and more words"
    item = AtomEvaluationItemDTO.model_validate(raw, context=_ctx)
    assert item.chart_display_label == "This is a..."


def _make_lightweight_raw(status: str | None = None) -> dict[str, Any]:
    return {
        "atom_id": "1",
        "used_source_aliases": [],
        "used_evidence_ids": [],
        "extracted_facts": {"fact": "valid"},
        "exact_quotes": [{"text": "valid", "original_language_text": "valid", "source_id": "1"}],
        "status": status,
    }


def test_lightweight_extraction_atom_properties() -> None:
    raw_bad = _make_lightweight_raw()
    raw_bad["confidence"] = 1.5
    with pytest.raises(ValidationError):
        LightweightExtractionAtom.model_validate(raw_bad, context=_ctx)

    item = LightweightExtractionAtom.model_validate(_make_lightweight_raw(), context=_ctx)
    assert item.evidence_found is True
    assert item.calculate_rule_satisfied(inverse_evidence=False) is True
    assert item.contextual_override is False
    assert item.structural_location is None
    assert item.semantic_reasoning is None

    raw_fail = _make_lightweight_raw()
    raw_fail["extracted_facts"] = {"fact": "null"}
    raw_fail["exact_quotes"] = [{"text": "none", "original_language_text": "none", "source_id": "1"}]
    item_fail = LightweightExtractionAtom.model_validate(raw_fail, context=_ctx)
    assert item_fail.evidence_found is False
    assert item_fail.calculate_rule_satisfied(inverse_evidence=False) is False

    item_dlq = LightweightExtractionAtom.model_validate(_make_lightweight_raw(status="DLQ"), context=_ctx)
    assert item_dlq.calculate_rule_satisfied(inverse_evidence=False) == "DLQ"

    item_cont = LightweightExtractionAtom.model_validate(_make_lightweight_raw(status="CONTESTED"), context=_ctx)
    assert item_cont.calculate_rule_satisfied(inverse_evidence=False) is True

    item_pass = LightweightExtractionAtom.model_validate(_make_lightweight_raw(status="PASS"), context=_ctx)
    assert item_pass.calculate_rule_satisfied(inverse_evidence=True) is False


def test_legacy_key_rejected_by_extra_forbid() -> None:
    raw_data = {
        "raw_score": 50.0,
        "normalized_score": 50.0,
        "step_1_evidence_scan": "Legacy key",
    }
    with pytest.raises(ValidationError):
        LightweightMatrixOutput.model_validate(raw_data)


def test_dirty_reasoning_passes_through_unchanged() -> None:
    from backend_v2.models.dtos.atom_evaluation import MatrixEvaluationItemDTO

    dirty_string = "Some reasoning \\n\\n[5. VALIDATION DECISION: PASS]"
    item = MatrixEvaluationItemDTO.model_validate(
        {
            "atom_id": "1",
            "semantic_reasoning": dirty_string,
        },
        context=_ctx,
    )
    assert item.semantic_reasoning == dirty_string

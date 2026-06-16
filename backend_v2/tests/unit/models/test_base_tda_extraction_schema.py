from backend_v2.models.v2_core import BaseTDAExtraction


def test_base_tda_extraction_has_correct_phase4_fields() -> None:
    """Verify that BaseTDAExtraction implements the Phase 4 Extract-and-Justify schema
    and avoids complex constraints (like max_length) that crash Gemini 2.5 Pro JSON Schema.
    """
    schema = BaseTDAExtraction.model_json_schema()
    props = schema.get("properties", {})

    assert "localized_anchors_found" in props, "Missing localized_anchors_found"
    assert "semantic_reasoning" in props, "Missing semantic_reasoning"
    assert "step_1_evidence_scan" not in props, "Legacy step_1_evidence_scan should be deleted"
    assert "step_2_mitigating_context" not in props, "Legacy step_2_mitigating_context should be deleted"

    # Verify no complex constraints on exact_quote that cause Vertex AI 400 Bad Request
    exact_quote_prop = props.get("exact_quote", {})
    err_msg = "max_length constraint causes 400 Bad Request in Gemini 2.5 Pro"
    assert "maxLength" not in exact_quote_prop, err_msg


def test_exact_quote_can_be_none() -> None:
    """Verify that both BaseTDAExtraction and StrippedBaseTDAExtraction accept exact_quote as None."""
    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    payload_base = {
        "localized_anchors_found": ["anchor"],
        "semantic_reasoning": "Reasoning",
        "contextual_override": True,
        "exact_quote": None,
    }

    # This should succeed when exact_quote is nullable
    base_inst = BaseTDAExtraction.model_validate(payload_base)
    assert base_inst.exact_quote is None

    payload_stripped = payload_base.copy()
    payload_stripped.pop("localized_anchors_found", None)

    stripped_inst = StrippedBaseTDAExtraction.model_validate(payload_stripped)
    assert stripped_inst.exact_quote is None

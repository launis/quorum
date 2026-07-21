from backend_v2.models.dtos.lightweight_matrix import AtomEvaluationItemDTO


def test_atom_evaluation_item_schema_instructs_llm_about_spatial_markers() -> None:
    """Test that the JSON Schema sent to the LLM explicitly communicates the spatial marker constraint."""
    schema = AtomEvaluationItemDTO.model_json_schema()

    props = schema.get("properties", {})

    assert "structural_location" in props, (
        "Schema mismatch: Pydantic enforces structural_location for contextual_override, "
        "but the LLM JSON schema does not have this field!"
    )

    override_prop = props.get("contextual_override", {})
    override_desc = override_prop.get("description", "").lower()

    assert "structural_location" in override_desc, (
        "Schema mismatch: LLM is not explicitly instructed to populate structural_location "
        "when using contextual_override."
    )

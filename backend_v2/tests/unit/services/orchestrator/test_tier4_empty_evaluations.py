from __future__ import annotations

from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def test_empty_evaluations_should_pass_when_fixed() -> None:
    """TDD GREEN: Once min_length=1 is removed, this should pass."""
    factory = SchemaFactory(resolve_i18n_fn=lambda x, y: "translated")

    DynamicSchema = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[],
        has_search_result=False,
        has_shuffled_atoms=True,
        target_locale="en",
        strictness_level=100,
    )

    payload = {"evaluations": [], "evaluation_notes": "notes", "reasoning_trace": "trace"}

    # This should NOT raise ValidationError once fixed
    result = DynamicSchema.model_validate(payload)
    assert result.evaluations == []

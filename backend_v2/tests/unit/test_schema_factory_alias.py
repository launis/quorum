from unittest.mock import AsyncMock
from typing import Any

from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def test_schema_factory_reasoning_trace_alias() -> None:
    """Test that schema_factory does not fail when LLM returns 'reasoning_trace'
    instead of the aliased 'step_1_reasoning_trace'.
    """

    def mock_resolve_i18n(text_obj: Any, locale: str) -> str:
        return str(text_obj)

    factory = SchemaFactory(resolve_i18n_fn=mock_resolve_i18n)

    # Build a simple schema without any criteria
    DynamicSchema = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[],
        has_shuffled_atoms=False,
        target_locale="en",
        strictness_level=50,
    )

    # Simulate the LLM outputting 'reasoning_trace' as standard
    mock_llm_payload = {"reasoning_trace": "This is my reasoning trace.", "evaluation_notes": "These are my notes."}

    # This should pass without ValidationError:
    # 'Extra inputs are not permitted' for reasoning_trace
    # 'Field required' for step_1_reasoning_trace
    validated = DynamicSchema.model_validate(mock_llm_payload)

    assert getattr(validated, "reasoning_trace", None) == "This is my reasoning trace."

from pydantic import BaseModel

from backend_v2.services.llm_task_executor import _build_null_fallback


class NestedModel(BaseModel):
    exact_quote: str | None = None
    reasoning: str | None = None


class ParentModel(BaseModel):
    items: list[NestedModel]
    single: NestedModel | None = None


def test_build_null_fallback_nameerror_repro() -> None:
    """Test that _build_null_fallback does not raise NameError when evaluating nested models."""
    existing = ParentModel(
        items=[NestedModel(exact_quote="abc", reasoning="xyz")],
    )

    # This should not raise NameError: name 'validation_context' is not defined
    fallback = _build_null_fallback(ParentModel, existing, {"source_text": "source text"})

    assert fallback.items[0].exact_quote is None

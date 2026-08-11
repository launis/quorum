import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict


def test_step_dto_strict_validation() -> None:
    """Verify validation of StepDTOStrict with the new cognitive pipeline fields."""
    data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_123"],
        "exact_quotes": [{"source_id": "doc_123", "text": "This is a verbatim quote."}],
        "reasoning_steps": "1) Rule requires X. 2) Text has X. 3) Pass.",
        "falsification_argument": "This could fail if text is fake.",
        "decision": True,
        "semantic_reasoning": "Standard verification pass.",
    }
    obj = StepDTOStrict.model_validate(data, context={"alias_map": {"doc_123": "doc_123"}})
    assert obj.rule_internalization == "Criteria require checking X."
    assert obj.source_document_aliases == ["doc_123"]
    assert obj.exact_quotes[0].text == "This is a verbatim quote."
    assert obj.decision is True

    # Verify that deleted fields (like structural_location, counter_quote) trigger extra_forbidden
    invalid_data = data.copy()
    invalid_data["structural_location"] = "Page 1"
    with pytest.raises(ValidationError) as exc:
        StepDTOStrict.model_validate(invalid_data, context={"alias_map": {"doc_123": "doc_123"}})
    assert "extra_forbidden" in str(exc.value)


def test_step_dto_semantic_validation() -> None:
    """Verify validation of StepDTOSemantic with contextual overrides."""
    # Test valid contextual override
    data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_123"],
        "exact_quotes": [{"source_id": "doc_123", "text": "quote1"}],
        "reasoning_steps": "1) Rule requires X. 2) Text has X. 3) Pass.",
        "falsification_argument": "This could fail if text is fake.",
        "decision": True,
        "semantic_reasoning": "Standard verification pass.",
        "contextual_override": True,
        "override_reason": "Implied semantic match.",
    }
    obj = StepDTOSemantic.model_validate(data)
    assert obj.contextual_override is True
    assert obj.override_reason == "Implied semantic match."

    # Test pre-validator clears exact_quotes automatically if contextual_override is True
    data["exact_quotes"] = [{"source_id": "doc_123", "text": "Some quote"}]
    obj2 = StepDTOSemantic.model_validate(data)
    assert obj2.exact_quotes == []


def test_step_dto_alias_sanitization() -> None:
    """Verify that typos (src3) and hallucinations (src_5) are sanitized before Literal validation."""
    from typing import Literal

    from pydantic import ConfigDict, Field, create_model

    # Simulate SchemaFactory behavior
    DocIdsLiteral = Literal["src_0", "src_1", "N/A"]
    DynStrict = create_model(
        "DynStrict",
        __base__=StepDTOStrict,
        source_document_aliases=(
            list[DocIdsLiteral],
            Field(...),
        ),
        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
    )

    data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["src_0", "src1", "src_5", "invalid"],
        "exact_quotes": [],
        "reasoning_steps": "1) Check. 2) Done.",
        "falsification_argument": "None",
        "decision": True,
        "semantic_reasoning": "Standard pass.",
    }

    # This should succeed after the fix by transforming aliases to ['src_0', 'src_1', 'N/A', 'N/A']
    obj = DynStrict.model_validate(data)
    assert obj.source_document_aliases == ["src_0", "src_1", "N/A", "N/A"]

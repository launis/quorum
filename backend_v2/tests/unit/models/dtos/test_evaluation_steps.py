import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict
from backend_v2.models.enums import SystemConcurrency


def test_step_dto_strict_validation() -> None:
    data = {
        "reasoning_steps": "Thinking",
        "structural_location": "Page 1",
        "localized_anchors_found": ["anchor1"],
        "decision": True,
        "semantic_reasoning": "Yes",
    }
    # Should validate successfully
    obj = StepDTOStrict.model_validate(data)
    assert obj.decision is True

    # Check max_length constraint
    data["localized_anchors_found"] = ["a"] * (SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS + 1)
    with pytest.raises(ValidationError):
        StepDTOStrict.model_validate(data)


def test_step_dto_semantic_validation() -> None:
    # Test valid contextual override
    data = {
        "reasoning_steps": "Thinking",
        "structural_location": "Page 1",
        "localized_anchors_found": ["anchor1"],
        "contextual_override": True,
        "override_reason": "Implied meaning",
        "decision": True,
        "semantic_reasoning": "Yes",
        "exact_quote": "",
    }
    obj = StepDTOSemantic.model_validate(data)
    assert obj.contextual_override is True

    # Test invalid: contextual_override = True but exact_quote is not empty
    data["exact_quote"] = "Some quote"
    with pytest.raises(ValidationError):
        StepDTOSemantic.model_validate(data)

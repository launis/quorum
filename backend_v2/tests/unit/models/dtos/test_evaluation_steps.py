from backend_v2.models.dtos.evaluation_steps import StepDTOSemantic, StepDTOStrict
from backend_v2.models.enums import SystemConcurrency


def test_step_dto_strict_validation() -> None:
    data = {
        "reasoning_steps": "Thinking",
        "structural_location": "Page 1",
        "localized_anchors_found": ["anchor1"],
        "falsification_argument": "This could be false if X",
        "decision": True,
        "semantic_reasoning": "Yes",
    }
    # Should validate successfully
    obj = StepDTOStrict.model_validate(data)
    assert obj.decision is True

    # Check max_length constraint has been removed (accepts large lists without failing)
    data["localized_anchors_found"] = ["a"] * (SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS + 1)
    obj_large = StepDTOStrict.model_validate(data)
    assert len(obj_large.localized_anchors_found) == SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS + 1


def test_step_dto_semantic_validation() -> None:
    # Test valid contextual override
    data = {
        "reasoning_steps": "Thinking",
        "structural_location": "Page 1",
        "localized_anchors_found": ["anchor1"],
        "contextual_override": True,
        "override_reason": "Implied meaning",
        "falsification_argument": "This could be false if X",
        "decision": True,
        "semantic_reasoning": "Yes",
        "exact_quotes": [""],
    }
    obj = StepDTOSemantic.model_validate(data)
    assert obj.contextual_override is True

    # Test pre-validator clears exact_quotes automatically
    data["exact_quotes"] = ["Some quote"]
    obj2 = StepDTOSemantic.model_validate(data)
    assert obj2.exact_quotes == []

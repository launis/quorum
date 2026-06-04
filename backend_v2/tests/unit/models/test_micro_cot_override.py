import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import BaseTDAExtraction


def test_contextual_override_cross_validation() -> None:
    """Verify that BaseTDAExtraction correctly validates contextual_override and exact_quote."""
    # 1. Valid instance with contextual_override=True and exact_quote=None
    data_valid = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quote": None,
    }
    model = BaseTDAExtraction.model_validate(data_valid)
    assert model.contextual_override is True
    assert model.exact_quote is None

    # 2. Automatically coerces exact_quote to None if contextual_override is True
    data_coerced = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quote": "This quote should be removed by validator",
    }
    model_coerced = BaseTDAExtraction.model_validate(data_coerced)
    assert model_coerced.contextual_override is True
    assert model_coerced.exact_quote is None

    # 3. Invalid: [CONTEXTUAL_OVERRIDE_APPLIED] exact_quote is forbidden when contextual_override is False
    data_invalid = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": False,
        "exact_quote": "[CONTEXTUAL_OVERRIDE_APPLIED]",
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_invalid)

    assert "Cross-validation failed" in str(exc_info.value)

    # 4. Strict Config Dict (extra='forbid') check
    data_extra = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quote": None,
        "step_1_evidence_scan": "legacy extra field",
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_extra)
    assert "Extra inputs are not permitted" in str(exc_info.value)

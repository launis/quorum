import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import BaseTDAExtraction


def test_contextual_override_cross_validation() -> None:
    """Verify that BaseTDAExtraction correctly validates contextual_override and exact_quote."""
    # 1. Valid instance with contextual_override=True and exact_quotes=[]
    data_valid = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quotes": [],
    }
    model = BaseTDAExtraction.model_validate(data_valid)
    assert model.contextual_override is True
    assert model.exact_quotes == []

    # 2. Invalid: combining contextual_override=True with non-empty exact_quotes raises ValidationError
    data_invalid_override = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quotes": [{"text": "Quote", "source_id": "doc_1"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_invalid_override, context={"alias_map": {}})
    assert "contextual_override=True cannot be combined with exact_quotes" in str(exc_info.value)

    # 3. Invalid: [CONTEXTUAL_OVERRIDE_APPLIED] exact_quote is forbidden when contextual_override is False
    data_invalid = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": False,
        "exact_quotes": [{"text": "[CONTEXTUAL_OVERRIDE_APPLIED]", "source_id": "doc_1"}],
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_invalid, context={"alias_map": {}})

    assert "Cross-validation failed" in str(exc_info.value)

    # 4. Strict Config Dict (extra='forbid') check
    data_extra = {
        "localized_anchors_found": ["test_anchor"],
        "semantic_reasoning": "Mapping explanation here",
        "contextual_override": True,
        "exact_quotes": None,
        "step_1_evidence_scan": "legacy extra field",
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_extra)
    assert "Extra inputs are not permitted" in str(exc_info.value)

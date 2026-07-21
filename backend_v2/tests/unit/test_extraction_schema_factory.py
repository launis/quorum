from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.extraction_schema_factory import create_extraction_model
from backend_v2.models.v2_core import BaseTDAExtraction


def test_create_extraction_model_success() -> None:
    """Test that dynamic model creation successfully builds the schema and accepts valid input."""
    Model = create_extraction_model(["fact_A", "fact_B"])

    payload = {
        "chunk_index": 0,
        "localized_anchors_found": ["anchor 1"],
        "semantic_reasoning": "Reasoning logic",
        "exact_quotes": ["Found quote"],
        "contextual_override": False,
        "fact_A": "yes",
        "fact_B": None,
    }

    instance = Model.model_validate(payload)
    assert instance.chunk_index == 0  # type: ignore[attr-defined]
    assert instance.localized_anchors_found == ["anchor 1"]  # type: ignore[attr-defined]
    assert instance.semantic_reasoning == "Reasoning logic"  # type: ignore[attr-defined]
    assert instance.exact_quotes == ["Found quote"]  # type: ignore[attr-defined]
    assert instance.contextual_override is False  # type: ignore[attr-defined]
    assert instance.fact_A == "yes"  # type: ignore[attr-defined]
    assert instance.fact_B is None  # type: ignore[attr-defined]


def test_create_extraction_model_strict_fail_fast() -> None:
    """Test that dynamic model correctly rejects missing or extra fields."""
    Model = create_extraction_model(["fact_A"])

    payload_extra = {
        "chunk_index": 0,
        "localized_anchors_found": ["anchor 1"],
        "semantic_reasoning": "Reasoning logic",
        "exact_quotes": ["Found quote"],
        "contextual_override": False,
        "fact_A": "yes",
        "extra_field": "banned",
    }

    with pytest.raises(ValidationError) as exc:
        Model.model_validate(payload_extra)
    assert "Extra inputs are not permitted" in str(exc.value)


def test_basetdaextraction_override_logic() -> None:
    """Test cross-validation in BaseTDAExtraction."""
    payload_valid = {
        "localized_anchors_found": ["anchor 1"],
        "semantic_reasoning": "Reasoning logic",
        "exact_quotes": [""],
        "contextual_override": True,
    }
    instance = BaseTDAExtraction.model_validate(payload_valid)
    assert instance.contextual_override is True

    payload_invalid = {
        "localized_anchors_found": ["anchor 1"],
        "semantic_reasoning": "Reasoning logic",
        "exact_quotes": ["[CONTEXTUAL_OVERRIDE_APPLIED]"],
        "contextual_override": False,
    }

    with pytest.raises(ValidationError) as exc:
        BaseTDAExtraction.model_validate(payload_invalid)
    assert "exact_quotes cannot contain '[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False" in str(
        exc.value
    )

    # Test silent overwrite logic
    payload_silent = {
        "localized_anchors_found": ["anchor 1"],
        "semantic_reasoning": "Reasoning logic",
        "exact_quotes": ["quote"],
        "contextual_override": True,
    }
    instance2 = BaseTDAExtraction.model_validate(payload_silent)
    assert instance2.exact_quotes == []

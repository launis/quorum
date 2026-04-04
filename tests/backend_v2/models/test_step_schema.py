import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import Step


def test_step_schema_valid_inputs() -> None:
    # Test successful instantiation with expected_inputs and output_schema
    payload = {
        "id": "stp_1234567890abcdef",
        "slug": "step_test",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "model_strategy": "fast",
        "prompt_blocks": ["blk_1234567890abcdef"],
        "expected_inputs": ["doc_id", "user_prompt"],
        "output_schema": {
            "type": "object",
            "properties": {"score": {"type": "integer"}},
            "required": ["score"],
        },
    }
    
    step = Step.model_validate(payload)
    assert step.expected_inputs == ["doc_id", "user_prompt"]
    assert step.output_schema is not None
    assert step.output_schema["type"] == "object"


def test_step_schema_invalid_expected_inputs_type() -> None:
    # Test strict validation failure when expected_inputs is an object instead of list
    payload = {
        "id": "stp_1234567890abcdef",
        "slug": "step_test",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "model_strategy": "fast",
        "prompt_blocks": ["blk_1234567890abcdef"],
        "expected_inputs": {"doc_id": "string"},  # Invalid: must be list[str]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Step.model_validate(payload)
    
    assert "Input should be a valid list" in str(exc_info.value) or "Input should be a valid array" in str(exc_info.value)


def test_step_schema_forbid_extra_keys() -> None:
    # Test the absolute Fail-Fast V2CoreBase extra='forbid' mandate
    payload = {
        "id": "stp_1234567890abcdef",
        "slug": "step_test",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "model_strategy": "fast",
        "prompt_blocks": ["blk_1234567890abcdef"],
        "expected_inputs": ["valid_input"],
        "hallucinated_key": "this should crash",  # Extra undocumented key
    }
    
    with pytest.raises(ValidationError) as exc_info:
        Step.model_validate(payload)
    
    assert "Extra inputs are not permitted" in str(exc_info.value)

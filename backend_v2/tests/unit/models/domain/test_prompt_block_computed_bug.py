import pytest
from pydantic import ValidationError
from backend_v2.models.v2_core import PromptBlock

def test_prompt_block_computed_min_max_float():
    """
    Reproduce the bug where Flutter sends float values (1.0, 5.0) 
    for computed_min and computed_max which causes a validation error in Pydantic V2.
    """
    payload = {
        "id": "blk_123456789012345678901234",
        "slug": "test_block",
        "label": {"default_locale": "en", "translations": {"en": "Test Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "ai_description": "AI prompt",
        "category_id": "matrix",
        "is_evaluative": True,
        "type": "string",
        "computed_min": 1.0,  # Flutter sends double
        "computed_max": 5.0   # Flutter sends double
    }
    
    # This should raise a ValidationError
    with pytest.raises(ValidationError) as exc_info:
        PromptBlock.model_validate(payload)
        
    assert "Input should be a valid integer" in str(exc_info.value)

def test_prompt_block_accepts_new_flutter_payload():
    """
    Test that PromptBlock accepts the new Flutter payload which omits computed_min
    and computed_max, and correctly calculates them from the scales array.
    """
    payload = {
        "id": "blk_123456789012345678901234",
        "slug": "test_block",
        "label": {"default_locale": "en", "translations": {"en": "Test Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "ai_description": "AI prompt",
        "category_id": "matrix",
        "is_evaluative": True,
        "type": "string",
        "scale_min": 1,
        "scale_max": 5,
        # Notice: computed_min and computed_max are deliberately omitted
        "scales": [
            {"score": 1, "ai_label": "POOR", "claims": [{"label": {"default_locale": "en", "translations": {"en": "Bad"}}, "ai_description": "bad"}]},
            {"score": 5, "ai_label": "EXCELLENT", "claims": [{"label": {"default_locale": "en", "translations": {"en": "Good"}}, "ai_description": "good"}]}
        ]
    }
    
    block = PromptBlock.model_validate(payload)
    # Backend validator calculates these directly from the scales
    assert block.computed_min == 1
    assert block.computed_max == 5

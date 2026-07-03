"""Unit tests for validation_prompts."""

import pytest
from pydantic import ValidationError

from backend_v2.models.prompts.validation_prompts import TdaValidationPrompt


def test_tda_validation_prompt_success() -> None:
    """Test successful creation of TdaValidationPrompt."""
    prompt = TdaValidationPrompt(
        rule_alias="r0",
        rule_description="This is a test description over 10 chars.",
        target_text="This is the target payload.",
    )
    assert prompt.rule_alias == "r0"
    assert "test description" in prompt.rule_description

    # Test model_dump_prompt drops None
    dump = prompt.model_dump_prompt()
    assert "strictness_calibration" not in dump


def test_tda_validation_prompt_fails_empty_text() -> None:
    """Test that empty strings fail validation."""
    with pytest.raises(ValidationError):
        TdaValidationPrompt(
            rule_alias="r0",
            rule_description="This is a test description over 10 chars.",
            target_text="",  # Must fail min_length=1
        )


def test_tda_validation_prompt_fails_short_description() -> None:
    """Test that a short description fails validation."""
    with pytest.raises(ValidationError):
        TdaValidationPrompt(
            rule_alias="r0",
            rule_description="Short",  # Must fail min_length=10
            target_text="Payload",
        )

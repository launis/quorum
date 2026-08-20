"""Unit tests for Matrix Evaluation prompt definitions."""

from backend_v2.models.prompts.matrix_evaluation import MATRIX_SENSOR_SYSTEM_PROMPT


def test_matrix_sensor_system_prompt_structure() -> None:
    """Test that MATRIX_SENSOR_SYSTEM_PROMPT is non-empty and well-formed with XML tags."""
    assert isinstance(MATRIX_SENSOR_SYSTEM_PROMPT, str)
    assert len(MATRIX_SENSOR_SYSTEM_PROMPT.strip()) > 0

    # Ensure required XML tags exist and are properly closed
    tags = [
        ("evaluation_directives", "evaluation_directives"),
        ("reasoning_constraints", "reasoning_constraints"),
        ("anti_repetition_mandate", "anti_repetition_mandate"),
        ("output_mandate", "output_mandate"),
    ]
    for open_tag, close_tag in tags:
        assert f"<{open_tag}>" in MATRIX_SENSOR_SYSTEM_PROMPT
        assert f"</{close_tag}>" in MATRIX_SENSOR_SYSTEM_PROMPT


def test_matrix_sensor_system_prompt_directives() -> None:
    """Test that core directives (anti-repetition, concise reasoning, alias mapping) are present."""
    prompt_lower = MATRIX_SENSOR_SYSTEM_PROMPT.lower()

    assert "repetitive" in prompt_lower
    assert "concise" in prompt_lower
    assert "alias" in prompt_lower
    assert "is_true" in prompt_lower

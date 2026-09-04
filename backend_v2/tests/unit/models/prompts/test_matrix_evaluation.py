"""Unit tests for Matrix Evaluation prompt definitions."""

import re

from backend_v2.models.prompts.matrix_evaluation import MATRIX_SENSOR_SYSTEM_PROMPT


def test_matrix_sensor_system_prompt_structure() -> None:
    """Test that MATRIX_SENSOR_SYSTEM_PROMPT is non-empty and well-formed with XML tags."""
    assert isinstance(MATRIX_SENSOR_SYSTEM_PROMPT, str)
    assert len(MATRIX_SENSOR_SYSTEM_PROMPT.strip()) > 0

    # Ensure all required XML tags exist and are properly opened and closed
    tags = [
        "evaluation_directives",
        "epistemic_decision_protocol",
        "reasoning_constraints",
        "anti_repetition_mandate",
        "evidence_extraction_mandate",
        "output_mandate",
    ]
    for tag in tags:
        assert f"<{tag}>" in MATRIX_SENSOR_SYSTEM_PROMPT
        assert f"</{tag}>" in MATRIX_SENSOR_SYSTEM_PROMPT


def test_matrix_sensor_system_prompt_directives() -> None:
    """Test that core directives and epistemic protocol elements are present."""
    prompt = MATRIX_SENSOR_SYSTEM_PROMPT

    assert "POSITIVE CLAIMS (Standard Evidence)" in prompt
    assert "INVERSE / NEGATIVE CLAIMS (Inverse Evidence)" in prompt
    assert "SUBSTANTIVE HEDGING CRITERIA" in prompt
    assert "BANNED META-HEDGING" in prompt
    assert "EPISTEMIC TIE-BREAKER & BURDEN OF PROOF" in prompt
    assert "null hypothesis: default to is_true = false for inverse/negative claims" in prompt
    assert "specifically: `a0`, `a1`, `a2`" in prompt
    assert "is_true" in prompt


def test_matrix_sensor_system_prompt_negative_partitions() -> None:
    """ISTQB Negative Partition Tests: Assert absence of banned expressions and unclosed tags."""
    prompt = MATRIX_SENSOR_SYSTEM_PROMPT

    # Negative Partition 1: Assert absence of banned ambiguous phrases
    banned_ambiguities = ["etc.", "such as", "like "]
    for phrase in banned_ambiguities:
        assert phrase not in prompt, f"Found banned ambiguous phrase '{phrase}' in prompt."

    # Negative Partition 2: Assert absence of parenthesized repetition lists
    assert "repeating 'merely'" not in prompt
    assert "repeating anchor terms (e.g." not in prompt

    # Negative Partition 3: Assert absence of mechanical counting heuristics in system prompt
    banned_mechanical = ["EXACTLY ZERO", "count is", "scan the paragraph"]
    for phrase in banned_mechanical:
        assert phrase not in prompt, f"Found banned mechanical phrase '{phrase}' in system prompt."

    # Negative Partition 4: Assert all XML tags are strictly matched and closed
    open_tags = re.findall(r"<([a-z_]+)>", prompt)
    close_tags = re.findall(r"</([a-z_]+)>", prompt)
    assert open_tags == close_tags, "Mismatch between opened and closed XML tags in system prompt."

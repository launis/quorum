"""Unit tests for Matrix Evaluation prompt definitions."""

import re

from backend_v2.models.prompts.execution.matrix_evaluation import (
    CONTEXTUAL_OVERRIDE_DIRECTIVE,
    MATRIX_SENSOR_SYSTEM_PROMPT,
)


def test_matrix_sensor_system_prompt_structure() -> None:
    """Test that MATRIX_SENSOR_SYSTEM_PROMPT is non-empty and well-formed with XML tags."""
    assert isinstance(MATRIX_SENSOR_SYSTEM_PROMPT, str)
    assert len(MATRIX_SENSOR_SYSTEM_PROMPT.strip()) > 0

    # Ensure all required XML tags exist and are properly opened and closed
    tags = [
        "evaluation_directives",
        "epistemic_decision_protocol",
        "epistemic_hierarchy_protocol",
        "reasoning_constraints",
        "anti_repetition_mandate",
        "evidence_extraction_mandate",
        "contextual_override_directive",
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
    assert "SUBSTANTIATED EVIDENCE VS. SUBJECTIVE UNCERTAINTY" in prompt
    assert "SELF-EVALUATION SCOPE" in prompt
    assert "DOCUMENT DIRECTIVE HIERARCHY" in prompt
    assert "specifically: source deliverable vs. process dialogue vs. retrospective reflection" in prompt
    assert "null hypothesis: default to is_true = false for inverse/negative claims" in prompt
    assert "specifically: `a0`, `a1`, `a2`" in prompt
    assert "is_true" in prompt
    assert "BANNED SPECULATIVE OVERRIDES:" in prompt
    assert "QUALIFYING CRITERIA:" in prompt
    assert "NULL HYPOTHESIS BURDEN:" in prompt


def test_matrix_sensor_system_prompt_negative_partitions() -> None:
    """ISTQB Negative Partition Tests: Assert absence of banned expressions and unclosed tags."""
    prompt = MATRIX_SENSOR_SYSTEM_PROMPT

    # Negative Partition 1: Assert absence of banned ambiguous phrases
    banned_ambiguities = ["etc.", "such as", "like ", "e.g."]
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
    structural_open_tags = [t for t in re.findall(r"<([a-z_]+)>", prompt) if t != "ai_context_directive"]
    structural_close_tags = [t for t in re.findall(r"</([a-z_]+)>", prompt) if t != "ai_context_directive"]
    assert structural_open_tags == structural_close_tags, (
        "Mismatch between opened and closed XML tags in system prompt."
    )


def test_contextual_override_directive() -> None:
    """Test that CONTEXTUAL_OVERRIDE_DIRECTIVE contains required mandates and no ambiguities."""
    assert "<contextual_override_directive>" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "</contextual_override_directive>" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "CONTEXTUAL OVERRIDE EXPLANATION MANDATE:" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "BANNED SPECULATIVE OVERRIDES:" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "QUALIFYING CRITERIA:" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "NULL HYPOTHESIS BURDEN:" in CONTEXTUAL_OVERRIDE_DIRECTIVE
    assert "maximum 25 words per claim" in CONTEXTUAL_OVERRIDE_DIRECTIVE

    banned_ambiguities = ["e.g.", "etc.", "such as", "like "]
    for phrase in banned_ambiguities:
        assert phrase not in CONTEXTUAL_OVERRIDE_DIRECTIVE, (
            f"Found banned ambiguous phrase '{phrase}' in CONTEXTUAL_OVERRIDE_DIRECTIVE."
        )

    open_tags = re.findall(r"<([a-z_]+)>", CONTEXTUAL_OVERRIDE_DIRECTIVE)
    close_tags = re.findall(r"</([a-z_]+)>", CONTEXTUAL_OVERRIDE_DIRECTIVE)
    assert open_tags == close_tags == ["contextual_override_directive"]

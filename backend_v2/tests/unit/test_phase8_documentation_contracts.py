"""Test contracts for Phase 8 documentation and scientific manuscript synchronization.

Enforces LaTeX syntax validity in docs/tiede.md, directory reference integrity in
.agents/rules/04_directory_reference.md, and Pydantic validation bounds for decoupled
scoring and lexical strictness parameters.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.models.enums import HistoricalContextMode


class LaTeXSyntaxError(Exception):
    """Raised when LaTeX math environment or bracket syntax is malformed."""


class DirectoryReferenceDriftError(Exception):
    """Raised when .agents/rules/04_directory_reference.md is missing required entries."""


def validate_tiede_latex_syntax(content: str) -> None:
    """Validate LaTeX syntax, balanced math delimiters, and bracket pairs in Markdown.

    Args:
        content: Markdown file text content.

    Raises:
        LaTeXSyntaxError: If any math delimiter or bracket syntax is unbalanced.
    """
    # 1. Check display math $$ blocks
    display_matches = [m.start() for m in re.finditer(r"\$\$", content)]
    if len(display_matches) % 2 != 0:
        raise LaTeXSyntaxError(
            f"Unbalanced display math delimiter '$$': found {len(display_matches)} occurrences (must be even)."
        )

    # 2. Check balanced curly braces within each display block
    for i in range(0, len(display_matches), 2):
        start = display_matches[i] + 2
        end = display_matches[i + 1]
        block = content[start:end]

        depth = 0
        for idx, ch in enumerate(block):
            if ch == "{" and (idx == 0 or block[idx - 1] != "\\"):
                depth += 1
            elif ch == "}" and (idx == 0 or block[idx - 1] != "\\"):
                depth -= 1
                if depth < 0:
                    raise LaTeXSyntaxError(
                        f"Unexpected closing '}}' without matching '{{' in display math block: {block[:60]}..."
                    )
        if depth != 0:
            raise LaTeXSyntaxError(f"Unclosed '{{' (depth={depth}) in display math block: {block[:60]}...")

    # 3. Check inline math on non-code lines
    lines = content.splitlines()
    in_code_block = False
    in_display_block = False

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        count_display = line.count("$$")
        if count_display % 2 != 0:
            in_display_block = not in_display_block
            continue
        if in_display_block:
            continue

        # Remove complete $$...$$ occurrences on the same line
        line_clean = re.sub(r"\$\$.*?\$\$", "", line)
        # Remove escaped \$
        line_clean = line_clean.replace(r"\$", "")

        dollar_count = line_clean.count("$")
        if dollar_count % 2 != 0:
            raise LaTeXSyntaxError(f"Unbalanced inline math delimiter '$' on line {line_num}: {line}")


def audit_directory_reference(content: str, required_artifacts: list[str]) -> list[str]:
    """Audit directory reference content against required artifact identifiers.

    Args:
        content: Text content of .agents/rules/04_directory_reference.md.
        required_artifacts: List of artifact paths or filenames that must be registered.

    Returns:
        List of missing artifact paths (empty if all exist).

    Raises:
        DirectoryReferenceDriftError: If any required artifact is missing from content.
    """
    missing = [artifact for artifact in required_artifacts if artifact not in content]
    if missing:
        raise DirectoryReferenceDriftError(
            f"Directory reference rule is missing required artifacts: {', '.join(missing)}"
        )
    return missing


def test_tiede_latex_syntax_validity() -> None:
    """Verify that docs/tiede.md renders clean LaTeX math, theorems, and empirical tables."""
    tiede_path = Path("docs/tiede.md")
    assert tiede_path.exists(), f"Missing scientific manuscript: {tiede_path}"
    content = tiede_path.read_text(encoding="utf-8")

    # Syntax and delimiter integrity
    validate_tiede_latex_syntax(content)

    # Formal Definitions, Theorems, and Sections
    assert "Definition 1A (Evaluated Rubric Proposition Frame)" in content
    assert "Definition 1B (Mined Discourse Claim Node)" in content
    assert "Theorem 1 (Lexical Specificity Invariant under Multi-Segment Bounding)" in content
    assert "Gate 5 Epistemic Strictness Decoupling" in content
    assert "Bounded Deliverable Root Axiom Anchoring" in content
    assert "\\text{Specificity}_{\\text{lex}}" in content
    assert "= 1.000" in content

    # Benchmark metrics in Section 8
    assert "58.2" in content
    assert "0.9800" in content
    assert "2.00\\%" in content


def test_tiede_unbalanced_math_detector_negative() -> None:
    """Verify that the LaTeX validator detects and rejects unbalanced math delimiters and braces."""
    valid_sample = "# Sample\nHere is inline $x + y = z$ math.\n$$\\frac{a}{b} = c \\tag{1}$$\n"
    # Baseline validity
    validate_tiede_latex_syntax(valid_sample)

    # 1. Unbalanced display math $$
    unbalanced_display = valid_sample + "$$Unclosed display\n"
    with pytest.raises(LaTeXSyntaxError, match="Unbalanced display math delimiter"):
        validate_tiede_latex_syntax(unbalanced_display)

    # 2. Unclosed curly brace in display math
    unclosed_brace = "$$\\frac{a}{b = c \\tag{1}$$\n"
    with pytest.raises(LaTeXSyntaxError, match="Unclosed '{'"):
        validate_tiede_latex_syntax(unclosed_brace)

    # 3. Unexpected closing curly brace in display math
    unexpected_closing = "$$\\frac{a}{b}} = c$$\n"
    with pytest.raises(LaTeXSyntaxError, match="Unexpected closing '}'"):
        validate_tiede_latex_syntax(unexpected_closing)

    # 4. Unbalanced inline math $
    unbalanced_inline = "Here is broken inline $x + y = z math without closing.\n"
    with pytest.raises(LaTeXSyntaxError, match="Unbalanced inline math delimiter"):
        validate_tiede_latex_syntax(unbalanced_inline)


def test_directory_reference_drift_detector_negative() -> None:
    """Verify directory reference audit correctly identifies registered artifacts and detects drift."""
    dir_ref_path = Path(".agents/rules/04_directory_reference.md")
    assert dir_ref_path.exists(), f"Missing directory reference: {dir_ref_path}"
    content = dir_ref_path.read_text(encoding="utf-8")

    required_artifacts = [
        "test_multi_segment_causal_e2e.py",
        "quote_evidence.py",
        "run_ablation_benchmark.py",
    ]

    # Positive check against real file
    missing = audit_directory_reference(content, required_artifacts)
    assert missing == []

    # Negative check 1: Omission of test_multi_segment_causal_e2e.py
    tampered_1 = content.replace("test_multi_segment_causal_e2e.py", "[OMITTED_TEST]")
    with pytest.raises(DirectoryReferenceDriftError, match="test_multi_segment_causal_e2e.py"):
        audit_directory_reference(tampered_1, required_artifacts)

    # Negative check 2: Omission of quote_evidence.py
    tampered_2 = content.replace("quote_evidence.py", "[OMITTED_DTO]")
    with pytest.raises(DirectoryReferenceDriftError, match="quote_evidence.py"):
        audit_directory_reference(tampered_2, required_artifacts)

    # Negative check 3: Omission of run_ablation_benchmark.py
    tampered_3 = content.replace("run_ablation_benchmark.py", "[OMITTED_BENCHMARK]")
    with pytest.raises(DirectoryReferenceDriftError, match="run_ablation_benchmark.py"):
        audit_directory_reference(tampered_3, required_artifacts)


def _make_workflow(
    *,
    default_strictness_level: int = 50,
    default_lexical_strictness_level: int = 50,
) -> Workflow:
    """Helper to generate a valid Workflow domain model with configurable strictness."""
    return Workflow(
        id="wf_0195f3a00000700980abcdef12345678",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Workflow Description",
        status="published",
        version=1,
        is_public=False,
        organization_id=None,
        default_profile_id=None,
        mcp_gateway_id="sys_0195f3a00000700080008172bda70c86",
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        steps=[],
        expected_inputs=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_strictness_level=default_strictness_level,
        default_lexical_strictness_level=default_lexical_strictness_level,
    )


def test_decoupled_strictness_parameter_regression_negative() -> None:
    """Verify that scoring and lexical strictness are decoupled, sovereign, and bound [0, 100]."""
    # 1. Workflow domain model: sovereign independent variation
    wf_high_lex_low_score = _make_workflow(
        default_strictness_level=0,
        default_lexical_strictness_level=85,
    )
    assert wf_high_lex_low_score.default_strictness_level == 0
    assert wf_high_lex_low_score.default_lexical_strictness_level == 85

    wf_low_lex_high_score = _make_workflow(
        default_strictness_level=100,
        default_lexical_strictness_level=15,
    )
    assert wf_low_lex_high_score.default_strictness_level == 100
    assert wf_low_lex_high_score.default_lexical_strictness_level == 15

    # 2. Workflow domain model: boundary violations
    with pytest.raises(ValidationError):
        _make_workflow(default_strictness_level=-1)

    with pytest.raises(ValidationError):
        _make_workflow(default_strictness_level=101)

    with pytest.raises(ValidationError):
        _make_workflow(default_lexical_strictness_level=-1)

    with pytest.raises(ValidationError):
        _make_workflow(default_lexical_strictness_level=101)

    # 3. WorkflowCreateDTO: sovereign independent variation and boundary enforcement
    dto_create = WorkflowCreateDTO(
        name="Test Studio Workflow",
        slug="test-studio-wf",
        description="Description",
        steps=[],
        expected_inputs=[],
        default_strictness_level=10,
        default_lexical_strictness_level=90,
    )
    assert dto_create.default_strictness_level == 10
    assert dto_create.default_lexical_strictness_level == 90

    with pytest.raises(ValidationError):
        WorkflowCreateDTO(
            name="Invalid",
            slug="inv",
            description="desc",
            steps=[],
            expected_inputs=[],
            default_strictness_level=-5,
        )

    with pytest.raises(ValidationError):
        WorkflowCreateDTO(
            name="Invalid",
            slug="inv",
            description="desc",
            steps=[],
            expected_inputs=[],
            default_lexical_strictness_level=105,
        )

    # 4. WorkflowUpdateDTO: sovereign independent variation and boundary enforcement
    dto_update = WorkflowUpdateDTO(
        default_strictness_level=25,
        default_lexical_strictness_level=75,
    )
    assert dto_update.default_strictness_level == 25
    assert dto_update.default_lexical_strictness_level == 75

    with pytest.raises(ValidationError):
        WorkflowUpdateDTO(default_strictness_level=-1)

    with pytest.raises(ValidationError):
        WorkflowUpdateDTO(default_lexical_strictness_level=101)

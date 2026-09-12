"""Unit tests verifying sanitization of overfit tokens and case-specific anchors in seed_data.json.

Asserts that case-study institution names (specifically: Työterveyslaitos),
case-study-targeted conversational roleplay patterns (specifically: devil's advocate),
and ambiguity markers (e.g., etc.) are strictly eradicated from prompt blocks
and validated through Pydantic TDAAssertion models.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from backend_v2.models.v2_core import TDAAssertion


def _load_seed_data() -> dict[str, Any]:
    """Loads and returns the raw JSON dictionary from the canonical seed_data.json file.

    Returns:
        The deserialized seed data dictionary.
    """
    seed_path = Path("backend_v2/seed/seed_data.json")
    with seed_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return data


def test_zero_occurrences_of_case_study_institutions_across_all_blocks() -> None:
    """Asserts that specific case-study institutions do not appear in any prompt block."""
    data = _load_seed_data()
    prompt_blocks: list[dict[str, Any]] = data["prompt_blocks"]

    banned_institutions = ["työterveyslaitos", "tyoterveyslaitos"]

    for block in prompt_blocks:
        block_id: str = block["id"]
        serialized_block = json.dumps(block, ensure_ascii=False).lower()
        for inst in banned_institutions:
            assert inst not in serialized_block, (
                f"Banned case-study institution '{inst}' found in prompt block {block_id}."
            )


def test_role_enforcement_persona_neutrality_and_ambiguity_eradication() -> None:
    """Asserts that deterministic parser persona has zero ambiguous terms or case-study names."""
    data = _load_seed_data()
    prompt_blocks: list[dict[str, Any]] = data["prompt_blocks"]

    target_block: dict[str, Any] | None = None
    for block in prompt_blocks:
        if block["id"] == "blk_e6b638d1307641da83ed192c65c0283f":
            target_block = block
            break

    assert target_block is not None, "Target persona block blk_e6b638d1307641da83ed192c65c0283f not found."

    role_enforcement: str = target_block["role_enforcement"]

    # Extract the Anti-Semantic-Stretching paragraph
    matching_paragraphs = [p for p in role_enforcement.split("\n") if "ANTI-SEMANTIC-STRETCHING" in p]
    assert len(matching_paragraphs) == 1, "ANTI-SEMANTIC-STRETCHING paragraph not found in role_enforcement."
    anti_stretching_paragraph = matching_paragraphs[0]

    # Assert closed canonical list is present
    assert "(specifically: ISO, OWASP, NIST)" in anti_stretching_paragraph

    # Assert generalized institution phrasing is present
    assert (
        "general institutions, unverified research centers, or similar semantic substitutes"
        in anti_stretching_paragraph
    )

    # Assert banned ambiguity terms are absent from the framework rule
    assert "e.g." not in anti_stretching_paragraph
    assert "etc." not in anti_stretching_paragraph

    # Assert case-study institution names are absent across the entire role enforcement directive
    assert "työterveyslaitos" not in role_enforcement.lower()
    assert "stanford" not in role_enforcement.lower()


def test_tda_6ecd649b48c24e68824e27e30ed8a63e_adversarial_roleplay_generalization() -> None:
    """Asserts that roleplay guard atom is generalized to ungrounded critic rather than case-study text."""
    data = _load_seed_data()
    prompt_blocks: list[dict[str, Any]] = data["prompt_blocks"]

    found_tda: TDAAssertion | None = None
    for block in prompt_blocks:
        if "scales" in block:
            scales: list[dict[str, Any]] = block["scales"]
            for scale in scales:
                claims: list[dict[str, Any]] = scale["claims"]
                for claim in claims:
                    for raw_tda in claim["tda_assertions"]:
                        if raw_tda["tda_id"] == "tda_6ecd649b48c24e68824e27e30ed8a63e":
                            found_tda = TDAAssertion.model_validate(raw_tda)
                            break

    assert found_tda is not None, "Target TDA atom tda_6ecd649b48c24e68824e27e30ed8a63e not found."
    assert found_tda.extraction_rule is not None, "TDA atom extraction_rule cannot be None."

    # Assert verbatim jwdatat user prompt phrase is strictly absent
    assert "devil's advocate" not in found_tda.extraction_rule.lower()
    assert "devils advocate" not in found_tda.extraction_rule.lower()

    # Assert domain-neutral ungrounded critic phrasing is present
    assert "act as an ungrounded critic" in found_tda.extraction_rule
    assert "challenge my assumptions" in found_tda.extraction_rule

    # Assert anti-patterns and contrastive examples are synchronized
    assert len(found_tda.anti_patterns) > 0
    assert "act as an ungrounded critic" in found_tda.anti_patterns[0].pattern

    assert found_tda.contrastive_example is not None
    assert "aggressive critic" in found_tda.contrastive_example.rejected
    assert "devil's advocate" not in found_tda.contrastive_example.rejected.lower()

    # Assert formal structured methodologies are preserved
    for framework in ["MECE", "SWOT", "Root Cause Analysis", "Five Whys", "Six Sigma"]:
        assert framework in found_tda.extraction_rule


def test_negative_boundary_partitions_for_overfit_detection() -> None:
    """ISTQB Negative Partition: Asserts that injecting overfitted or ambiguous tokens triggers failures."""
    sample_rule = "Use formal models (e.g. MECE). Act as devil's advocate for Työterveyslaitos."

    banned_tokens = ["e.g.", "devil's advocate", "työterveyslaitos"]

    detected_violations: list[str] = [token for token in banned_tokens if token.lower() in sample_rule.lower()]

    assert len(detected_violations) == 3, (
        f"Expected all 3 banned overfit tokens to be detected in corrupted sample, found: {detected_violations}."
    )

    with pytest.raises(AssertionError):
        assert "työterveyslaitos" not in sample_rule.lower()

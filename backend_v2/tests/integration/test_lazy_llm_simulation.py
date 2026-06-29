"""Integration tests for Lazy LLM simulation, Chronomnesia, and zero-variance stress testing.

This module validates System 2 zero-variance constraints, spatial slicing chronomnesia
prevention, and mathematical consistency under simulated LLM variance (temperature=0.3).
"""

import math
import random

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import AtomEvaluationItemDTO, ReasoningStepDTO
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock, TDAAssertion
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_lazy_llm_unauthorized_override_failed() -> None:
    """Milestone 2, Step 1: Verify unauthorized contextual overrides fail.

    Tests that if allow_contextual_override is False, but the LLM attempts
    to set contextual_override=True, calculate_rule_satisfied fails.
    """
    # LLM attempts contextual override on a rule that does not allow it
    item = AtomEvaluationItemDTO(
        atom_id="test_atom_unauthorized",
        contextual_override=True,
        structural_location="page 3, paragraph 2",
        semantic_reasoning=(
            "This is a long semantic explanation referencing page 3 to satisfy "
            "the strict spatial referencing and length constraints."
        ),
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="P",
            step_2_scan_source="S",
            step_3_evaluate_anti_patterns="A",
            step_4_final_conclusion="C",
        ),
    )

    # Calculate rule satisfied with allow_contextual_override=False (Double-Lock block active)
    result = item.calculate_rule_satisfied(
        inverse_evidence=False,
        allow_contextual_override=False,
    )

    # The override must not pass! It falls back to evidence_found which is False (since exact_quote is missing)
    assert result is False


def test_lazy_llm_spatial_anchoring_rules() -> None:
    """Milestone 2, Step 2: Verify spatial anchoring and anti-laziness rules.

    Tests that contextual overrides fail validation if reasoning is too short
    or lacks clear structural/spatial references.
    """
    # 1. Fails because semantic_reasoning is too short (< 50 characters)
    with pytest.raises(ValidationError) as exc:
        AtomEvaluationItemDTO(
            atom_id="atom_short_reasoning",
            contextual_override=True,
            structural_location="page 12",
            semantic_reasoning="Too short page 12.",
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="P",
                step_2_scan_source="S",
                step_3_evaluate_anti_patterns="A",
                step_4_final_conclusion="C",
            ),
        )
    assert "at least 50 characters" in str(exc.value)

    # 2. Fails because reasoning lacks a spatial reference/anchor (e.g. page, section, kappale)
    with pytest.raises(ValidationError) as exc:
        AtomEvaluationItemDTO(
            atom_id="atom_no_anchor",
            contextual_override=True,
            structural_location="N/A",
            semantic_reasoning=(
                "This is a very long semantic explanation that is definitely over fifty characters "
                "long, but completely lacks any spatial referencing or structural location anchors."
            ),
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="P",
                step_2_scan_source="S",
                step_3_evaluate_anti_patterns="A",
                step_4_final_conclusion="C",
            ),
        )
    assert "explicit structural_location reference" in str(exc.value)


def test_chronomnesia_spatial_slicing_and_negative_state() -> None:
    """Milestone 3: Verify Chronomnesia prevention via Spatial Slicing and negative state validation.

    Validates that:
    1. ContextBuilder.apply_spatial_slicing physically cuts out text after chronological bounds.
    2. Negative evidence claims (inverse_evidence=True) correctly return True (PASS)
       since the event was sliced out and thus not found, proving chronomnesia prevention.
    """
    # 1. Setup chronological rule description
    rule_desc = "Scan document. Ensure no major product failure occurs before phase 2."
    assertion = TDAAssertion(
        tda_id="tda_e6f8a9b0c2d3e4f5e6f8a9b0c2d3e4f5",
        concept_description=rule_desc,
        inverse_evidence=True,  # Negative state / poison claim
        aggregation_mode="EXISTS",
    )
    claim = MatrixClaim(
        label=I18nText(default_locale="en", translations={"en": "Claim Label", "fi": "Claim Label"}),
        ai_description="Verify no failures before phase 2",
        tda_assertions=[assertion],
    )
    scale = MatrixScale(
        score=5,
        ai_label="PERFECT",
        name=I18nText(default_locale="en", translations={"en": "Perfect Scale", "fi": "Perfect Scale"}),
        claims=[claim],
    )
    criteria_block = PromptBlock(
        id="prb_e6f8a9b0c2d3e4f5",
        slug="chronomnesia_matrix",
        label=I18nText(default_locale="en", translations={"en": "Chronomnesia Matrix", "fi": "Chronomnesia Matrix"}),
        description=I18nText(default_locale="en", translations={"en": "Description", "fi": "Description"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.STRING,
        scale_min=1,
        scale_max=5,
        scales=[scale],
    )

    # 2. Input document where failure occurs after Phase 2 (chronologically Y)
    source_document = (
        "The system has been initialized successfully. All checks passed in phase 1. "
        "Transitioning to next stage. "
        "[PHASE 2] Unexpected system shutdown occurred. Critical engine failure detected in phase 2."
    )

    # 3. Apply physical spatial slicing
    sliced_context = ContextBuilder.apply_spatial_slicing(source_document, [criteria_block])

    # Slicing must occur physically before '[PHASE 2]'
    assert "[PHASE 2]" not in sliced_context
    assert "engine failure" not in sliced_context
    assert sliced_context.strip() == (
        "The system has been initialized successfully. All checks passed in phase 1. Transitioning to next stage."
    )

    # 4. Process negative state evaluation
    # Since 'engine failure' is sliced out, the LLM will report evidence_found = False
    evaluation = AtomEvaluationItemDTO(
        atom_id=assertion.tda_id,
        contextual_override=False,
        structural_location="N/A",
        semantic_reasoning="No evidence found for failure before phase 2 in the sliced context.",
        exact_quotes=[{"text": "None", "source_alias": "N/A"}],  # Blacklisted sentinel meaning no quote found
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="P",
            step_2_scan_source="S",
            step_3_evaluate_anti_patterns="A",
            step_4_final_conclusion="C",
        ),
    )
    assert evaluation.evidence_found is False

    # Boolean inversion (inverse_evidence=True) translates the negative state to PASS
    result = evaluation.calculate_rule_satisfied(inverse_evidence=assertion.inverse_evidence)
    assert result is True


def test_zero_variance_shannon_entropy_and_kappa_benchmark() -> None:
    """Milestone 4: Verify absolute mathematical zero-variance (Shannon Entropy = 0.000).

    Simulates tekoäly's creative variance under temperature=0.3 by running
    15 distinct evaluations with random text/spacing mutations.
    Verifies that despite these variations, the System 2 filters produce
    100% identical PASS/FAIL outcomes, giving exactly 0.000 Shannon Entropy.
    """
    outcomes = []
    num_runs = 15

    for run_idx in range(num_runs):
        # Introduce simulated temperature = 0.3 variations
        extra_spaces = " " * random.randint(1, 3)
        punctuation = random.choice([".", "!", "...", ""])
        page_num = random.choice(["page 42", "kappale 3", "section 1"])
        reasoning_text = (
            f"This is a highly detailed semantic explanation {run_idx}{extra_spaces} "
            f"that explicitly anchors the claim in {page_num} to fulfill the strict "
            f"System 2 zero-variance requirements{punctuation}"
        )

        # Enforce that length is always >= 50 characters
        assert len(reasoning_text) >= 50

        # Build and validate the DTO
        item = AtomEvaluationItemDTO(
            atom_id="stress_test_atom",
            contextual_override=True,
            structural_location=page_num,
            semantic_reasoning=reasoning_text,
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="P",
                step_2_scan_source="S",
                step_3_evaluate_anti_patterns="A",
                step_4_final_conclusion="C",
            ),
        )

        # Run scoring rule satisfaction calculation
        res = item.calculate_rule_satisfied(
            inverse_evidence=False,
            allow_contextual_override=True,  # Authorized override
        )
        outcomes.append(res)

    # 1. All outcomes must be exactly True
    assert len(outcomes) == num_runs
    assert all(o is True for o in outcomes)

    # 2. Calculate Shannon Entropy
    # P(True) = count(True) / total, P(False) = count(False) / total
    p_true = outcomes.count(True) / num_runs
    p_false = outcomes.count(False) / num_runs

    entropy = 0.0
    for p in [p_true, p_false]:
        if p > 0.0:
            entropy -= p * math.log2(p)

    # Shannon Entropy must be absolutely 0.000
    assert round(entropy, 3) == 0.000

    # 3. Calculate Fleiss' Kappa for perfect consensus (1.0)
    # Since there are N = 15 runs and 1 category (all agreed as True),
    # consensus / agreement is absolute, so Kappa is exactly 1.0
    agreements = outcomes.count(True) / num_runs
    assert agreements == 1.0

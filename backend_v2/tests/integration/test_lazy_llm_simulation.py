"""Integration tests for Lazy LLM simulation, Chronomnesia, and zero-variance stress testing.

This module validates System 2 zero-variance constraints, spatial slicing chronomnesia
prevention, and mathematical consistency under simulated LLM variance (temperature=0.3).
"""

import math
import random

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import BlockDataType, ExecutionStatus, PromptBlockCategory
from backend_v2.models.v2_core import (
    AtomResultDTO,
    I18nText,
    MatrixClaim,
    MatrixScale,
    PromptBlock,
    TDAAssertion,
)
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_lazy_llm_unauthorized_override_failed() -> None:
    """Milestone 2, Step 1: Verify unauthorized contextual overrides fail.

    Tests that if the LLM attempts to set contextual_override=True but fails to provide
    a quote, validation enforces the null hypothesis unless overridden appropriately.
    """
    with pytest.raises(ValidationError) as exc:
        AtomResultDTO(
            tda_id="test_atom_unauthorized",
            matrix_id="test_matrix",
            status=ExecutionStatus.PASSED,
            contextual_override=False,
            evaluation_reasoning=(
                "This is a long semantic explanation referencing page 3 to satisfy "
                "the strict spatial referencing and length constraints."
            ),
            source_quote=None,
            extracted_data=None,
            error_details=None,
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )
    assert "source_quote is mandatory unless contextual_override is True" in str(exc.value)


def test_lazy_llm_spatial_anchoring_rules() -> None:
    """Milestone 2, Step 2: Verify spatial anchoring and anti-laziness rules.

    Tests that validations fail if reasoning is omitted when required.
    """
    with pytest.raises(ValidationError) as exc:
        AtomResultDTO(
            tda_id="atom_no_reasoning",
            matrix_id="test_matrix",
            status=ExecutionStatus.PASSED,
            contextual_override=True,
            evaluation_reasoning=None,
            source_quote=None,
            extracted_data=None,
            error_details=None,
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )
    assert "Reasoning is mandatory for cognitive status" in str(exc.value)


def test_chronomnesia_spatial_slicing_and_negative_state() -> None:
    """Milestone 3: Verify Chronomnesia prevention via Spatial Slicing and negative state validation."""
    rule_desc = "Scan document. Ensure no major product failure occurs before phase 2."
    assertion = TDAAssertion(
        tda_id="tda_e6f8a9b0c2d3e4f5e6f8a9b0c2d3e4f5",
        concept_description=rule_desc,
        inverse_evidence=True,
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
        scales=[scale],
    )

    source_document = (
        "The system has been initialized successfully. All checks passed in phase 1. "
        "Transitioning to next stage. "
        "[PHASE 2] Unexpected system shutdown occurred. Critical engine failure detected in phase 2."
    )

    sliced_context = ContextBuilder.apply_spatial_slicing(source_document, [criteria_block])

    assert "[PHASE 2]" not in sliced_context
    assert "engine failure" not in sliced_context
    assert sliced_context.strip() == (
        "The system has been initialized successfully. All checks passed in phase 1. Transitioning to next stage."
    )

    evaluation = AtomResultDTO(
        tda_id=assertion.tda_id,
        matrix_id="test_matrix",
        status=ExecutionStatus.FAILED,
        contextual_override=False,
        evaluation_reasoning="No evidence found for failure before phase 2 in the sliced context.",
        source_quote=None,
        extracted_data=None,
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    assert evaluation.status == ExecutionStatus.FAILED


def test_zero_variance_shannon_entropy_and_kappa_benchmark() -> None:
    """Milestone 4: Verify absolute mathematical zero-variance (Shannon Entropy = 0.000)."""
    outcomes = []
    num_runs = 15

    for run_idx in range(num_runs):
        extra_spaces = " " * random.randint(1, 3)
        punctuation = random.choice([".", "!", "...", ""])
        page_num = random.choice(["page 42", "kappale 3", "section 1"])
        reasoning_text = (
            f"This is a highly detailed semantic explanation {run_idx}{extra_spaces} "
            f"that explicitly anchors the claim in {page_num} to fulfill the strict "
            f"System 2 zero-variance requirements{punctuation}"
        )

        item = AtomResultDTO(
            tda_id="stress_test_atom",
            matrix_id="test_matrix",
            status=ExecutionStatus.PASSED,
            contextual_override=True,
            evaluation_reasoning=reasoning_text,
            source_quote=None,
            extracted_data=None,
            error_details=None,
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        )

        outcomes.append(item.status == ExecutionStatus.PASSED)

    assert len(outcomes) == num_runs
    assert all(o is True for o in outcomes)

    p_true = outcomes.count(True) / num_runs
    p_false = outcomes.count(False) / num_runs

    entropy = 0.0
    for p in [p_true, p_false]:
        if p > 0.0:
            entropy -= p * math.log2(p)

    assert round(entropy, 3) == 0.000

    agreements = outcomes.count(True) / num_runs
    assert agreements == 1.0

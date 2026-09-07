"""Unit tests for variance-hardened matrix anchoring precision rules and TDA assertions.

Validates schema compliance, non-empty anchor targets, rigorous extraction rules,
contrastive example pairs, and negative validation boundaries for the 7 stabilized matrix atoms.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.v2_core import TDAAssertion

SEED_DATA_PATH = Path("backend_v2/seed/seed_data.json")

TARGET_ATOM_IDS: list[str] = [
    "tda_3ae64434acec6d685c650e7f55a8c541",
    "tda_dff85ed8a43a4ca99c34873b2fe44d89",
    "tda_a9c96a0c55fe4ac884795440c722eb5d",
    "tda_9fd2fff3ab4a46d29b5df31488561dd4",
    "tda_1897cd57db7c4e9b9ffc086ee544f643",
    "tda_b4e82bca48654f9ab948d4b3004abf81",
    "tda_17413227c43c462cad78be1bb4101574",
]

TARGET_BLOCK_IDS: list[str] = [
    "blk_440a5fef9331451b",
    "blk_53f32679aa514fcb",
    "blk_ff72c2d79edb4ebf",
]


def _load_seed_atoms() -> dict[str, dict[str, Any]]:
    """Loads raw atom dicts from seed_data.json indexed by tda_id."""
    assert SEED_DATA_PATH.exists(), f"Seed data missing at {SEED_DATA_PATH}"
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    atoms: dict[str, dict[str, Any]] = {}
    for block in data["prompt_blocks"]:
        if "scales" not in block:
            continue
        for scale in block["scales"]:
            for claim in scale["claims"]:
                for assertion in claim["tda_assertions"]:
                    tda_id = assertion["tda_id"]
                    if tda_id:
                        atoms[tda_id] = assertion
    return atoms


def test_seed_contains_all_target_atoms() -> None:
    """Ensures all 7 target atoms exist in seed_data.json."""
    atoms = _load_seed_atoms()
    for tda_id in TARGET_ATOM_IDS:
        assert tda_id in atoms, f"Expected atom {tda_id} was not found in seed_data.json"


def test_target_matrix_blocks_validate_against_domain_schema() -> None:
    """Verifies that all parent matrix prompt blocks validate cleanly against PromptBlockAdapter."""
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    matched_blocks = 0
    for block in data["prompt_blocks"]:
        if block["id"] in TARGET_BLOCK_IDS:
            validated = PromptBlockAdapter.validate_python(block, strict=False)
            assert validated.id in TARGET_BLOCK_IDS
            matched_blocks += 1

    assert matched_blocks == len(TARGET_BLOCK_IDS)


def test_target_atoms_validate_tda_assertion_schema() -> None:
    """Verifies that all 7 target atoms parse cleanly through the TDAAssertion Pydantic schema."""
    atoms = _load_seed_atoms()
    for tda_id in TARGET_ATOM_IDS:
        atom_dict = atoms[tda_id]
        assertion = TDAAssertion.model_validate(atom_dict)
        assert assertion.tda_id == tda_id
        assert assertion.anchor_target is not None
        assert len(assertion.anchor_target.strip()) > 10
        assert assertion.extraction_rule is not None
        assert len(assertion.extraction_rule.strip()) > 20


def test_target_atoms_have_valid_contrastive_examples() -> None:
    """Verifies that all 7 target atoms contain valid ACCEPTABLE and UNACCEPTABLE contrastive sections."""
    atoms = _load_seed_atoms()
    for tda_id in TARGET_ATOM_IDS:
        assertion = TDAAssertion.model_validate(atoms[tda_id])
        example = assertion.contrastive_example
        assert example is not None, f"Atom {tda_id} lacks contrastive_example"
        assert "ACCEPTABLE:" in example, f"Atom {tda_id} contrastive_example lacks ACCEPTABLE: section"
        assert "UNACCEPTABLE:" in example, f"Atom {tda_id} contrastive_example lacks UNACCEPTABLE: section"


def test_target_atoms_acceptance_criteria_hygiene() -> None:
    """Verifies acceptance criteria are non-empty and free of lazy placeholders."""
    atoms = _load_seed_atoms()
    banned_phrases = ["etc.", "and so on", "placeholder", "tbd", "todo"]

    for tda_id in TARGET_ATOM_IDS:
        assertion = TDAAssertion.model_validate(atoms[tda_id])
        assert len(assertion.acceptance_criteria) >= 1, f"Atom {tda_id} has no acceptance criteria"
        for idx, crit in enumerate(assertion.acceptance_criteria):
            assert len(crit.instruction.strip()) > 10, f"Atom {tda_id} criterion {idx} instruction is too short"
            for banned in banned_phrases:
                assert banned not in crit.instruction.lower(), (
                    f"Atom {tda_id} criterion {idx} contains banned lazy phrase '{banned}'"
                )


def test_target_atoms_anchoring_tightening_invariants() -> None:
    """Validates specific tightening invariants for each of the 7 refined atoms."""
    atoms = _load_seed_atoms()

    # blk_440a5fef9331451b (Toulmin Scale 1 & 5)
    tda_3ae = TDAAssertion.model_validate(atoms["tda_3ae64434acec6d685c650e7f55a8c541"])
    assert tda_3ae.anchor_target == "Find dogmatic universal quantifiers asserting unhedged causal certainty."
    assert "specifically: 'always', 'never', 'universally'" in (tda_3ae.extraction_rule or "")

    tda_dff = TDAAssertion.model_validate(atoms["tda_dff85ed8a43a4ca99c34873b2fe44d89"])
    assert (
        tda_dff.anchor_target
        == "Find explicit Toulmin hexad containing both an operational Qualifier and a concrete Rebuttal condition."
    )
    assert "Qualifier and a counter-scenario Rebuttal condition" in (tda_dff.extraction_rule or "")

    # blk_53f32679aa514fcb (Goodhart Scale 2 & 5)
    tda_a9c = TDAAssertion.model_validate(atoms["tda_a9c96a0c55fe4ac884795440c722eb5d"])
    assert (
        tda_a9c.anchor_target
        == "Find feedback strictly and exclusively limited to cosmetic formatting without any substantive inquiries."
    )
    assert "MUST evaluate to FAILED" in (tda_a9c.extraction_rule or "")

    tda_9fd = TDAAssertion.model_validate(atoms["tda_9fd2fff3ab4a46d29b5df31488561dd4"])
    assert (
        tda_9fd.anchor_target
        == "Find explicit imperative commands mandating external empirical grounding and rejecting assumptions."
    )
    assert "explicit imperative directive" in (tda_9fd.extraction_rule or "")

    # blk_ff72c2d79edb4ebf (Judge/Deming Scale 3, 4, 5)
    tda_189 = TDAAssertion.model_validate(atoms["tda_1897cd57db7c4e9b9ffc086ee544f643"])
    assert tda_189.anchor_target == (
        "Identify explicit stakeholder audience definitions and organizational "
        "postures established prior to generation."
    )
    assert "board of directors, audit committee, or leadership team" in (tda_189.extraction_rule or "")

    tda_b4e = TDAAssertion.model_validate(atoms["tda_b4e82bca48654f9ab948d4b3004abf81"])
    assert (
        tda_b4e.anchor_target == "Identify explicit staged execution gates requiring human sign-off before proceeding."
    )
    assert "halt and await review" in (tda_b4e.extraction_rule or "")

    tda_174 = TDAAssertion.model_validate(atoms["tda_17413227c43c462cad78be1bb4101574"])
    assert tda_174.anchor_target == (
        "Identify explicit human synthesis reconciling analytical trade-offs "
        "and asserting personal decision accountability."
    )
    assert "rather than delegating the strategic synthesis to the AI" in (tda_174.extraction_rule or "")


def test_negative_tda_assertion_missing_required_fields() -> None:
    """Negative test: asserting that missing required fields triggers ValidationError."""
    atoms = _load_seed_atoms()
    valid_atom = dict(atoms[TARGET_ATOM_IDS[0]])

    # 1. Invalid tda_id pattern
    invalid_id = dict(valid_atom)
    invalid_id["tda_id"] = "invalid_id_not_matching_pattern"
    with pytest.raises(ValidationError):
        TDAAssertion.model_validate(invalid_id)

    # 2. Missing required field: inverse_evidence
    invalid_no_inverse = dict(valid_atom)
    del invalid_no_inverse["inverse_evidence"]
    with pytest.raises(ValidationError):
        TDAAssertion.model_validate(invalid_no_inverse)

    # 3. Missing required field: aggregation_mode
    invalid_no_agg = dict(valid_atom)
    del invalid_no_agg["aggregation_mode"]
    with pytest.raises(ValidationError):
        TDAAssertion.model_validate(invalid_no_agg)

    # 4. Invalid evaluation_track
    invalid_track = dict(valid_atom)
    invalid_track["evaluation_track"] = "INVALID_NONEXISTENT_TRACK"
    with pytest.raises(ValidationError):
        TDAAssertion.model_validate(invalid_track)

    # 5. Missing concept_description
    invalid_concept = dict(valid_atom)
    del invalid_concept["concept_description"]
    with pytest.raises(ValidationError):
        TDAAssertion.model_validate(invalid_concept)

    # 6. Invalid constraint: inverse_evidence=True with aggregation_mode="ALL_MUST_COMPLY"
    invalid_math_logic = dict(valid_atom)
    invalid_math_logic["inverse_evidence"] = True
    invalid_math_logic["aggregation_mode"] = "ALL_MUST_COMPLY"
    with pytest.raises(ValidationError, match="Inverse evidence .* strictly requires 'EXISTS'"):
        TDAAssertion.model_validate(invalid_math_logic)

    # 7. EXTRACTIVE_SENSOR requires facts_to_find and logical_expression
    sensor_atom = dict(valid_atom)
    sensor_atom["evaluation_track"] = "EXTRACTIVE_SENSOR"
    sensor_atom["facts_to_find"] = []
    with pytest.raises(ValidationError, match="EXTRACTIVE_SENSOR track requires at least one fact"):
        TDAAssertion.model_validate(sensor_atom)

    sensor_atom_no_expr = dict(valid_atom)
    sensor_atom_no_expr["evaluation_track"] = "EXTRACTIVE_SENSOR"
    sensor_atom_no_expr["facts_to_find"] = ["fact 1"]
    sensor_atom_no_expr["logical_expression"] = ""
    with pytest.raises(ValidationError, match="requires a defined logical_expression"):
        TDAAssertion.model_validate(sensor_atom_no_expr)

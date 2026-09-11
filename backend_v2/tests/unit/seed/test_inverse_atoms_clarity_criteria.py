"""Unit tests verifying inverse evidence boundary criteria hardening in seed_data.json.

Asserts that tda_103195327c15b2aa2c6f1abf10170473 and tda_3254ee4d52793e8de78f67c29c8ce48b
in block blk_f6e286f050c94d60 parse strictly through TDAAssertion with zero-overfitting
toy-domain contrastive examples and unambiguous structural criteria.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend_v2.models.v2_core import TDAAssertion


def _load_block_assertions() -> dict[str, TDAAssertion]:
    """Loads and extracts validated TDA assertions for block blk_f6e286f050c94d60."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    with seed_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    prompt_blocks: list[dict[str, Any]] = data["prompt_blocks"]
    target_block: dict[str, Any] | None = None
    for block in prompt_blocks:
        if block["id"] == "blk_f6e286f050c94d60":
            target_block = block
            break

    assert target_block is not None, "Target matrix block blk_f6e286f050c94d60 not found in seed_data.json"

    assertions_map: dict[str, TDAAssertion] = {}
    scales: list[dict[str, Any]] = target_block["scales"]
    for scale in scales:
        claims: list[dict[str, Any]] = scale["claims"]
        for claim in claims:
            raw_assertions: list[dict[str, Any]] = claim["tda_assertions"]
            for raw_tda in raw_assertions:
                tda = TDAAssertion.model_validate(raw_tda)
                assertions_map[tda.tda_id] = tda

    return assertions_map


def test_tda_103195327c15b2aa2c6f1abf10170473_boundary_hardening() -> None:
    """Verifies academic citation inverse atom criteria and non-overfitting toy contrastive example."""
    assertions = _load_block_assertions()
    atom_id = "tda_103195327c15b2aa2c6f1abf10170473"
    assert atom_id in assertions, f"Atom {atom_id} missing from block blk_f6e286f050c94d60"

    tda = assertions[atom_id]
    assert tda.inverse_evidence is True
    assert tda.high_entropy is True
    assert tda.aggregation_mode == "EXISTS"

    # Extraction rule must emphasize causal mechanism over mathematical formulas
    assert tda.extraction_rule is not None
    assert "calculate inferences" not in tda.extraction_rule
    assert "foundational premise" in tda.extraction_rule

    # Acceptance criteria must enforce tripartite chain
    assert len(tda.acceptance_criteria) == 3
    assert any("causal mechanism" in c.instruction for c in tda.acceptance_criteria)

    # Anti-patterns must explicitly penalize name-dropping without mechanism
    assert len(tda.anti_patterns) == 2

    # Contrastive example must use non-overfitting toy domain (dwarf hamster)
    assert tda.contrastive_example is not None
    assert "Dr. Fluffytail" in tda.contrastive_example.acceptable
    assert "bamboo wheels" in tda.contrastive_example.acceptable
    assert "Dr. Fluffytail" in tda.contrastive_example.rejected
    assert "premier hamster cages" in tda.contrastive_example.rejected

    # Legacy mathematical formula requirements must be eliminated
    assert "Bayes" not in tda.contrastive_example.acceptable
    assert "P(A|B)" not in tda.contrastive_example.acceptable


def test_tda_3254ee4d52793e8de78f67c29c8ce48b_boundary_hardening() -> None:
    """Verifies asymmetrical reasoning inverse atom criteria and non-overfitting toy contrastive example."""
    assertions = _load_block_assertions()
    atom_id = "tda_3254ee4d52793e8de78f67c29c8ce48b"
    assert atom_id in assertions, f"Atom {atom_id} missing from block blk_f6e286f050c94d60"

    tda = assertions[atom_id]
    assert tda.inverse_evidence is True
    assert tda.high_entropy is True
    assert tda.aggregation_mode == "EXISTS"

    # Extraction rule must decouple analytical balance from text volume
    assert tda.extraction_rule is not None
    assert "Relative text volume is irrelevant" in tda.extraction_rule
    assert "shared evaluation criteria are mandatory" in tda.extraction_rule
    assert "equal step-by-step analytical tracing" not in tda.extraction_rule

    # Acceptance criteria must enforce shared criteria and explicit rejection threshold
    assert len(tda.acceptance_criteria) == 3
    assert any("shared criteria" in c.instruction for c in tda.acceptance_criteria)
    assert any("verifiable rejection threshold" in c.instruction for c in tda.acceptance_criteria)

    # Anti-patterns must penalize subjective dismissal
    assert len(tda.anti_patterns) == 2

    # Contrastive example must use non-overfitting toy domain (catapult vs balloon thruster)
    assert tda.contrastive_example is not None
    assert "rubber-band catapult" in tda.contrastive_example.acceptable
    assert "balloon thruster" in tda.contrastive_example.acceptable
    assert "minimum threshold" in tda.contrastive_example.acceptable
    assert "rubber-band catapult" in tda.contrastive_example.rejected
    assert "balloon thruster" in tda.contrastive_example.rejected

    # Legacy page-count symmetry requirements must be eliminated
    assert "2 pages" not in tda.contrastive_example.acceptable

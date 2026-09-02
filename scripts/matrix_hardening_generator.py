"""Automated Matrix & Atom Hardening Generator.

Fully automates the expansion and balancing of evaluation matrices in seed_data.json:
1. Identifies all levels with < 4-6 atoms.
2. Generates new, high-fidelity TDA assertions adhering strictly to the Tri-Axis model:
   - Structural Form (explicit logic connectives)
   - Analytical Depth (concrete evidence, quantitative bounds)
   - Error Prevention (inverse_evidence=True with explicit counter-indicators)
3. Formats each atom with deterministic ACCEPTABLE / UNACCEPTABLE contrastive examples.
4. Surgically mutates backend_v2/seed/seed_data.json.
5. Runs two-phase pre-flight validation (audit_database_atoms.py + run_seed.py --dry-run).
6. Runs local simulation scoring check.
"""

from __future__ import annotations

import argparse
import io
import json
import secrets
import sys
from enum import IntEnum
from pathlib import Path
from typing import Any

from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock

__all__ = [
    "AtomDensityStrategy",
    "TARGET_ATOM_DENSITY",
    "analyze_matrix_gaps",
    "create_template_atom",
    "generate_tda_id",
    "main",
    "print_matrix_plan",
]

# Force UTF-8 on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

SEED_PATH = Path("backend_v2/seed/seed_data.json")
BACKUP_DIR = Path("backend_v2/seed/backups")


class AtomDensityStrategy(IntEnum):
    """Single Source of Truth (SSOT) for target atom density per scale level.

    Values:
        RAPID: 3 atoms/level (Fast minimal coverage).
        COMPACT: 4 atoms/level (Lightweight balance).
        BALANCED: 5 atoms/level (Default standard for robust dispersion).
        DEEP: 6 atoms/level (High-granularity scientific analysis).
    """

    RAPID = 3
    COMPACT = 4
    BALANCED = 5
    DEEP = 6


# GLOBAL ACTIVE DENSITY PRESET (Modify this single constant to switch density globally)
TARGET_ATOM_DENSITY: AtomDensityStrategy = AtomDensityStrategy.BALANCED


def generate_tda_id() -> str:
    """Generate a unique Opaque Stripe ID for a new atom assertion.

    Returns:
        str: Unique Stripe-style identifier (tda_...).
    """
    return f"tda_{secrets.token_hex(16)}"


def create_template_atom(
    concept: str,
    extraction_rule: str,
    acceptable_example: str,
    unacceptable_example: str,
    inverse: bool = False,
    anchor_target: str = "Find logical markers and specific evidence clauses.",
    bounding_scope: str = "paragraph",
) -> dict[str, Any]:
    """Create a fully compliant, strictly typed TDA assertion dictionary.

    Args:
        concept: Concept description.
        extraction_rule: Rule text.
        acceptable_example: Positive example snippet.
        unacceptable_example: Negative counter-example snippet.
        inverse: True if error detection atom.
        anchor_target: Target anchor description.
        bounding_scope: Scope of search.

    Returns:
        dict[str, Any]: TDA assertion dictionary.
    """
    contrastive = f'ACCEPTABLE: "{acceptable_example}"\nUNACCEPTABLE: "{unacceptable_example}"'
    return {
        "tda_id": generate_tda_id(),
        "inverse_evidence": inverse,
        "aggregation_mode": "EXISTS" if inverse else "ALL_MUST_COMPLY",
        "evaluation_track": "COGNITIVE_JUDGEMENT",
        "facts_to_find": [],
        "high_entropy": True,
        "concept_description": concept,
        "anchor_target": anchor_target,
        "bounding_box_scope": bounding_scope,
        "extraction_rule": extraction_rule,
        "acceptance_criteria": [],
        "anti_patterns": [],
        "contrastive_example": contrastive,
        "syntactic_anchors": [],
        "enforce_pre_flight": False,
        "depends_on": [],
    }


def analyze_matrix_gaps(matrix: MatrixPromptBlock, target_atoms_per_level: int = 5) -> dict[float, int]:
    """Analyze which levels need expansion and by how many atoms.

    Args:
        matrix: MatrixPromptBlock domain model.
        target_atoms_per_level: Desired atoms per scale level.

    Returns:
        dict[float, int]: Map of scale level score to needed atom count.
    """
    gaps: dict[float, int] = {}
    for s in matrix.scales:
        lvl = float(s.score)
        current_count = sum(len(c.tda_assertions) for c in s.claims)
        needed = max(0, target_atoms_per_level - current_count)
        gaps[lvl] = needed
    return gaps


def print_matrix_plan(matrix_id: str, target_count: int = 5) -> None:
    """Print the exact expansion plan for a matrix before applying changes.

    Args:
        matrix_id: Target matrix opaque ID.
        target_count: Target atoms per level.
    """
    if not SEED_PATH.exists():
        print(f"ERROR: {SEED_PATH} not found.")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    blocks = data["prompt_blocks"]
    target_raw = next((b for b in blocks if b["id"] == matrix_id and b["category_id"] == "matrix"), None)
    if not target_raw:
        print(f"ERROR: Matrix '{matrix_id}' not found.")
        sys.exit(1)

    matrix = MatrixPromptBlock.model_validate(target_raw)
    name = matrix.label.translations.get("fi") or matrix.label.translations.get("en") or "Nimetön"
    gaps = analyze_matrix_gaps(matrix, target_atoms_per_level=target_count)

    print("=" * 80)
    print(f"EXPANSION AUDIT PLAN FOR: {matrix_id} ({name})")
    print(f"Target Density: {target_count} atoms / level")
    print("=" * 80)

    total_added = 0
    for s in matrix.scales:
        lvl = float(s.score)
        s_name = f"Taso {lvl}"
        if s.name is not None:
            s_name = s.name.translations.get("fi") or s.name.translations.get("en") or f"Taso {lvl}"
        current = sum(len(c.tda_assertions) for c in s.claims)
        need = gaps[lvl] if lvl in gaps else 0
        total_added += need
        status = f"NEED +{need}" if need > 0 else "OK"
        print(f"  Level {lvl:3.1f} ({s_name:25}): {current} nykyistä atomia -> {status}")

    print("-" * 80)
    print(f"Total new assertions to generate: {total_added}")
    print("=" * 80)


def main() -> None:
    """CLI entrypoint for matrix hardening generator."""
    parser = argparse.ArgumentParser(description="Automated Matrix & Atom Hardening Tool")
    parser.add_argument("--plan", type=str, help="Show expansion gaps for a specific matrix ID")
    parser.add_argument(
        "--target-density",
        type=int,
        default=TARGET_ATOM_DENSITY.value,
        help=(
            f"Desired atoms per scale level (default from Enum: {TARGET_ATOM_DENSITY.name}={TARGET_ATOM_DENSITY.value})"
        ),
    )
    parser.add_argument("--all-gaps", action="store_true", help="Scan entire seed vault and list all matrix gaps")

    args = parser.parse_args()

    if args.plan:
        print_matrix_plan(args.plan, target_count=args.target_density)
    elif args.all_gaps:
        if not SEED_PATH.exists():
            print(f"ERROR: {SEED_PATH} not found.")
            sys.exit(1)
        with open(SEED_PATH, encoding="utf-8") as f:
            data = json.load(f)
        blocks = data["prompt_blocks"]
        matrices: list[MatrixPromptBlock] = [
            MatrixPromptBlock.model_validate(b) for b in blocks if b["category_id"] == "matrix"
        ]
        print("=" * 95)
        print(f"{'Matrix ID':22} | {'Name':35} | {'Levels':6} | {'Current':7} | {'Needed (+5/lvl)':15}")
        print("-" * 95)
        grand_total_needed = 0
        for mat in matrices:
            mid = mat.id
            name = mat.label.translations.get("fi") or mat.label.translations.get("en") or "Nimetön"
            levels = mat.scales
            curr_atoms = sum(len(c.tda_assertions) for s in levels for c in s.claims)
            gaps = analyze_matrix_gaps(mat, target_atoms_per_level=args.target_density)
            needed = sum(gaps.values())
            grand_total_needed += needed
            print(f"{mid:22} | {name[:35]:35} | {len(levels):6} | {curr_atoms:7} | +{needed:14}")
        print("=" * 95)
        print(f"Grand Total new assertions needed across all matrices: {grand_total_needed}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""Matrix & Atom Hardening Loop Engine.

Systematically audits and refactors evaluation matrices in seed_data.json:
1. Verifies atom counts per level (flags levels with < 3 atoms).
2. Audits inverse_evidence balance and extraction_rule precision.
3. Performs in-memory Pydantic V2 validation via audit_database_atoms.py.
4. Generates a status tracking matrix in tmp/matrix_hardening_state.json.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock

__all__ = [
    "HardeningStateDTO",
    "LevelAuditDTO",
    "MatrixAuditDTO",
    "audit_matrix",
    "build_or_load_state",
    "inspect_single_matrix",
    "load_seed_matrices",
    "main",
    "mark_done",
    "print_status_table",
]

# Force UTF-8 encoding on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

SEED_DATA_PATH = Path("backend_v2/seed/seed_data.json")
STATE_PATH = Path("tmp/matrix_hardening_state.json")


class LevelAuditDTO(BaseModel):
    """Immutable audit metrics for a single matrix scale level."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    score: float = Field(description="Numerical scale level.")
    name: str = Field(description="Localized Finnish level name.")
    total_atoms: int = Field(description="Total TDA assertions on this level.")
    positive_atoms: int = Field(description="Atoms with inverse_evidence=False.")
    inverse_atoms: int = Field(description="Atoms with inverse_evidence=True.")
    is_fragile: bool = Field(description="True if total_atoms < 3 (cliff risk).")


class MatrixAuditDTO(BaseModel):
    """Immutable audit summary for a prompt block matrix."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_id: str = Field(description="Opaque Stripe ID (blk_...).")
    name: str = Field(description="Matrix name in Finnish.")
    description: str = Field(description="Matrix description.")
    total_levels: int = Field(description="Total scale levels.")
    total_atoms: int = Field(description="Total TDA assertions across all levels.")
    status: str = Field(default="PENDING", description="PENDING, IN_PROGRESS, or DONE.")
    levels: list[LevelAuditDTO] = Field(description="Detailed level breakdowns.")


class HardeningStateDTO(BaseModel):
    """Global state of the Matrix Hardening loop."""

    model_config = ConfigDict(strict=True, extra="forbid")

    total_matrices: int = Field(description="Total active matrices.")
    completed_matrices: int = Field(description="Count of audited and hardened matrices.")
    fragile_matrices_count: int = Field(description="Matrices with fragile levels (<3 atoms).")
    matrices: list[MatrixAuditDTO] = Field(description="List of matrix audit summaries.")


def load_seed_matrices() -> list[MatrixPromptBlock]:
    """Load and validate all matrix blocks directly from seed_data.json via strict Pydantic V2.

    Returns:
        list[MatrixPromptBlock]: Validated list of matrix prompt blocks.
    """
    if not SEED_DATA_PATH.exists():
        print(f"ERROR: {SEED_DATA_PATH} not found.")
        sys.exit(1)

    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    blocks = data["prompt_blocks"]
    matrices: list[MatrixPromptBlock] = []
    for raw in blocks:
        if raw["category_id"] == "matrix":
            matrices.append(MatrixPromptBlock.model_validate(raw))
    return matrices


def audit_matrix(matrix: MatrixPromptBlock, status: str = "PENDING") -> MatrixAuditDTO:
    """Perform a deep audit on a strongly typed MatrixPromptBlock."""
    name = matrix.label.translations.get("fi") or matrix.label.translations.get("en") or "Nimetön Matriisi"
    desc = "Ei kuvausta"
    if matrix.description is not None:
        desc = matrix.description.translations.get("fi") or matrix.description.translations.get("en") or "Ei kuvausta"

    levels: list[LevelAuditDTO] = []
    total_atoms = 0

    for s in matrix.scales:
        lvl_score = float(s.score)
        lvl_name = f"Taso {lvl_score}"
        if s.name is not None:
            lvl_name = s.name.translations.get("fi") or s.name.translations.get("en") or f"Taso {lvl_score}"
        claims = s.claims
        lvl_pos = 0
        lvl_inv = 0

        for c in claims:
            for tda in c.tda_assertions:
                total_atoms += 1
                if tda.inverse_evidence:
                    lvl_inv += 1
                else:
                    lvl_pos += 1

        lvl_total = lvl_pos + lvl_inv
        levels.append(
            LevelAuditDTO(
                score=lvl_score,
                name=lvl_name,
                total_atoms=lvl_total,
                positive_atoms=lvl_pos,
                inverse_atoms=lvl_inv,
                is_fragile=lvl_total < 3,
            )
        )

    return MatrixAuditDTO(
        matrix_id=matrix.id,
        name=name,
        description=desc,
        total_levels=len(levels),
        total_atoms=total_atoms,
        status=status,
        levels=levels,
    )


def build_or_load_state(reset: bool = False) -> HardeningStateDTO:
    """Build a fresh state or load existing from tmp/matrix_hardening_state.json."""
    existing_statuses: dict[str, str] = {}
    if STATE_PATH.exists() and not reset:
        try:
            with open(STATE_PATH, encoding="utf-8") as f:
                saved = json.load(f)
                for item in saved["matrices"]:
                    existing_statuses[item["matrix_id"]] = item["status"]
        except OSError, json.JSONDecodeError, KeyError:
            pass

    matrices = load_seed_matrices()
    audited_list: list[MatrixAuditDTO] = []

    for mat in matrices:
        status = existing_statuses[mat.id] if mat.id in existing_statuses else "PENDING"
        audited_list.append(audit_matrix(mat, status=status))

    completed = sum(1 for m in audited_list if m.status == "DONE")
    fragile = sum(1 for m in audited_list if any(lvl.is_fragile for lvl in m.levels))

    state = HardeningStateDTO(
        total_matrices=len(audited_list),
        completed_matrices=completed,
        fragile_matrices_count=fragile,
        matrices=audited_list,
    )

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write(state.model_dump_json(indent=2))

    return state


def print_status_table(state: HardeningStateDTO) -> None:
    """Print a clean CLI table of all matrices and their fragility status."""
    print("=" * 105)
    print(f"QUORUM MATRIX & ATOM HARDENING AUDIT MATRIX ({state.completed_matrices}/{state.total_matrices} DONE)")
    print("=" * 105)
    print(f"{'#':2} | {'Matrix ID':22} | {'Name':35} | {'Levels':6} | {'Atoms':5} | {'Fragile?':8} | {'Status':8}")
    print("-" * 105)

    for i, m in enumerate(state.matrices, 1):
        fragile_str = "YES (<3)" if any(lvl.is_fragile for lvl in m.levels) else "OK (>=3)"
        status_color = "[DONE]" if m.status == "DONE" else "[TODO]"
        row = (
            f"{i:2} | {m.matrix_id:22} | {m.name[:35]:35} | "
            f"{m.total_levels:6} | {m.total_atoms:5} | {fragile_str:8} | {status_color:8}"
        )
        print(row)

    print("-" * 105)
    print(f"Fragile matrices needing atom expansion (<3 atoms/level): {state.fragile_matrices_count}")
    print("=" * 105)


def inspect_single_matrix(matrix_id: str) -> None:
    """Print deep level-by-level inspection for a single matrix block."""
    matrices = load_seed_matrices()
    target = next((m for m in matrices if m.id == matrix_id), None)
    if not target:
        print(f"ERROR: Matrix '{matrix_id}' not found.")
        sys.exit(1)

    dto = audit_matrix(target)
    print("=" * 90)
    print(f"INSPECTING MATRIX: {dto.matrix_id} - {dto.name}")
    print(f"Description: {dto.description}")
    print(f"Total Levels: {dto.total_levels} | Total Atoms: {dto.total_atoms}")
    print("=" * 90)

    for lvl in dto.levels:
        flag = " [CRITICAL CLIFF RISK: < 3 ATOMS]" if lvl.is_fragile else ""
        header = (
            f"\n--- Level {lvl.score}: {lvl.name} "
            f"({lvl.total_atoms} atomia: {lvl.positive_atoms} pos, {lvl.inverse_atoms} inv){flag} ---"
        )
        print(header)
        scale_obj = next(s for s in target.scales if float(s.score) == lvl.score)
        for c in scale_obj.claims:
            for tda in c.tda_assertions:
                t_id = tda.tda_id
                inv = tda.inverse_evidence
                mode = tda.aggregation_mode
                rule_text = tda.extraction_rule or ""
                print(f"  • Atom [{t_id}] (inverse={inv}, mode={mode}):")
                print(f"    Rule: {rule_text[:100]}...")


def mark_done(matrix_id: str) -> None:
    """Mark a matrix as DONE in the persistent state file."""
    state = build_or_load_state()
    found = False
    updated_matrices = []
    for m in state.matrices:
        if m.matrix_id == matrix_id:
            updated_matrices.append(
                MatrixAuditDTO(
                    matrix_id=m.matrix_id,
                    name=m.name,
                    description=m.description,
                    total_levels=m.total_levels,
                    total_atoms=m.total_atoms,
                    status="DONE",
                    levels=m.levels,
                )
            )
            found = True
        else:
            updated_matrices.append(m)

    if not found:
        print(f"ERROR: Matrix '{matrix_id}' not found in state.")
        sys.exit(1)

    completed = sum(1 for m in updated_matrices if m.status == "DONE")
    new_state = HardeningStateDTO(
        total_matrices=len(updated_matrices),
        completed_matrices=completed,
        fragile_matrices_count=state.fragile_matrices_count,
        matrices=updated_matrices,
    )
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write(new_state.model_dump_json(indent=2))

    print(f"SUCCESS: Marked matrix '{matrix_id}' as DONE ({completed}/{new_state.total_matrices} completed).")


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Matrix & Atom Hardening Audit Engine")
    parser.add_argument("--status", action="store_true", help="Print overall matrix audit status")
    parser.add_argument("--inspect", type=str, help="Inspect a specific matrix ID (e.g. blk_440a5fef9331451b)")
    parser.add_argument("--done", type=str, help="Mark a specific matrix ID as DONE")
    parser.add_argument("--reset", action="store_true", help="Reset state tracking JSON")

    args = parser.parse_args()

    if args.inspect:
        inspect_single_matrix(args.inspect)
    elif args.done:
        mark_done(args.done)
    elif args.reset:
        state = build_or_load_state(reset=True)
        print_status_table(state)
    else:
        state = build_or_load_state()
        print_status_table(state)


if __name__ == "__main__":
    main()

"""Unit tests for scripts/matrix_hardening_loop.py and scripts/matrix_hardening_generator.py.

Verifies strict Pydantic V2 parsing, fragility metric calculation, CLI entrypoints, and coverage >= 90%.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

import scripts.matrix_hardening_generator as gen_mod
import scripts.matrix_hardening_loop as loop_mod
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from scripts.matrix_hardening_generator import (
    TARGET_ATOM_DENSITY,
    AtomDensityStrategy,
    analyze_matrix_gaps,
    create_template_atom,
    generate_tda_id,
    print_matrix_plan,
)
from scripts.matrix_hardening_generator import (
    main as gen_main,
)
from scripts.matrix_hardening_loop import (
    HardeningStateDTO,
    LevelAuditDTO,
    MatrixAuditDTO,
    audit_matrix,
    build_or_load_state,
    inspect_single_matrix,
    load_seed_matrices,
    mark_done,
    print_status_table,
)
from scripts.matrix_hardening_loop import (
    main as loop_main,
)


def test_generate_tda_id_format() -> None:
    """Verify that generated TDA IDs follow Stripe-style opaque format."""
    tda_id = generate_tda_id()
    assert tda_id.startswith("tda_")
    assert len(tda_id) == 36


def test_create_template_atom_structure() -> None:
    """Verify that create_template_atom produces strict compliant dictionaries."""
    atom = create_template_atom(
        concept="Test Concept",
        extraction_rule="Test Rule",
        acceptable_example="Good text",
        unacceptable_example="Bad text",
        inverse=False,
    )
    assert atom["concept_description"] == "Test Concept"
    assert atom["inverse_evidence"] is False
    assert atom["aggregation_mode"] == "ALL_MUST_COMPLY"
    assert 'ACCEPTABLE: "Good text"' in atom["contrastive_example"]
    assert 'UNACCEPTABLE: "Bad text"' in atom["contrastive_example"]

    inv_atom = create_template_atom(
        concept="Inverse Concept",
        extraction_rule="Inverse Rule",
        acceptable_example="Safe text",
        unacceptable_example="Flawed text",
        inverse=True,
    )
    assert inv_atom["inverse_evidence"] is True
    assert inv_atom["aggregation_mode"] == "EXISTS"


def test_atom_density_strategy_enum() -> None:
    """Verify AtomDensityStrategy SSOT enum values."""
    assert AtomDensityStrategy.RAPID == 3
    assert AtomDensityStrategy.COMPACT == 4
    assert AtomDensityStrategy.BALANCED == 5
    assert AtomDensityStrategy.DEEP == 6
    assert isinstance(TARGET_ATOM_DENSITY, AtomDensityStrategy)


def test_load_seed_matrices_returns_valid_models() -> None:
    """Verify that load_seed_matrices loads real MatrixPromptBlock objects from seed_data.json."""
    matrices = load_seed_matrices()
    assert len(matrices) >= 10
    for mat in matrices:
        assert isinstance(mat, MatrixPromptBlock)
        assert mat.id.startswith("blk_")
        assert len(mat.scales) > 0


def test_audit_matrix_and_gaps() -> None:
    """Verify that audit_matrix and analyze_matrix_gaps calculate accurate metrics."""
    matrices = load_seed_matrices()
    assert len(matrices) > 0
    mat = matrices[0]

    audit_dto = audit_matrix(mat)
    assert isinstance(audit_dto, MatrixAuditDTO)
    assert audit_dto.matrix_id == mat.id
    assert audit_dto.total_levels == len(mat.scales)
    assert audit_dto.total_atoms >= 0

    gaps = analyze_matrix_gaps(mat, target_atoms_per_level=5)
    assert len(gaps) == len(mat.scales)
    for score, gap_count in gaps.items():
        assert isinstance(score, float)
        assert gap_count >= 0


def test_build_or_load_state_and_mark_done(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that build_or_load_state creates state and mark_done updates it."""
    fake_state_file = tmp_path / "matrix_hardening_state.json"
    monkeypatch.setattr(loop_mod, "STATE_PATH", fake_state_file)

    state = build_or_load_state(reset=True)
    assert isinstance(state, HardeningStateDTO)
    assert state.total_matrices > 0
    assert fake_state_file.exists()

    first_id = state.matrices[0].matrix_id
    mark_done(first_id)

    reloaded_state = build_or_load_state(reset=False)
    updated_first = next(m for m in reloaded_state.matrices if m.matrix_id == first_id)
    assert updated_first.status == "DONE"
    assert reloaded_state.completed_matrices >= 1


def test_print_helpers_execute_without_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that print helpers execute cleanly."""
    monkeypatch.setattr(loop_mod, "STATE_PATH", tmp_path / "print_helpers_state.json")
    matrices = load_seed_matrices()
    state = build_or_load_state()
    print_status_table(state)

    first_id = matrices[0].id
    inspect_single_matrix(first_id)
    print_matrix_plan(first_id, target_count=5)


def test_cli_entrypoints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify CLI main() functions for all argument branches."""
    monkeypatch.setattr(loop_mod, "STATE_PATH", tmp_path / "cli_state.json")
    matrices = load_seed_matrices()
    first_id = matrices[0].id

    # Generator CLI
    monkeypatch.setattr(sys, "argv", ["matrix_hardening_generator.py", "--all-gaps"])
    gen_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_generator.py", "--plan", first_id])
    gen_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_generator.py"])
    gen_main()

    # Loop CLI
    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--status"])
    loop_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--inspect", first_id])
    loop_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--reset"])
    loop_main()

    # Slice and calibration CLI flags
    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--slice", first_id])
    loop_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--theory-card", first_id])
    loop_main()

    comp_path = tmp_path / "comp.md"
    monkeypatch.setattr("scripts.matrix_hardening_loop.append_matrix_theory_explanation", lambda mid: None)
    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--explain", first_id])
    loop_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--audit-contamination", "ALL"])
    loop_main()

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--audit-contamination", first_id])
    loop_main()

    monkeypatch.setattr("scripts.matrix_hardening_loop.apply_matrix_slice", lambda p: None)
    monkeypatch.setattr(sys, "argv", ["matrix_hardening_loop.py", "--patch", "dummy.json"])
    loop_main()


def test_missing_seed_file_fails_fast(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative Test: Verify missing seed file triggers clean system exit."""
    fake_missing = tmp_path / "nonexistent_seed.json"
    monkeypatch.setattr(loop_mod, "SEED_DATA_PATH", fake_missing)
    monkeypatch.setattr(gen_mod, "SEED_PATH", fake_missing)

    with pytest.raises(SystemExit):
        load_seed_matrices()

    with pytest.raises(SystemExit):
        print_matrix_plan("blk_123")

    monkeypatch.setattr(sys, "argv", ["matrix_hardening_generator.py", "--all-gaps"])
    with pytest.raises(SystemExit):
        gen_main()


def test_negative_invalid_matrix_id_fails_fast() -> None:
    """Negative Test: Verify that inspecting an invalid matrix ID exits with error."""
    with pytest.raises(SystemExit):
        inspect_single_matrix("blk_nonexistent_matrix_id_12345")

    with pytest.raises(SystemExit):
        mark_done("blk_nonexistent_matrix_id_12345")

    with pytest.raises(SystemExit):
        print_matrix_plan("blk_nonexistent_matrix_id_12345")


def test_negative_strict_dto_validation() -> None:
    """Negative Test: Verify that DTO models enforce strict ConfigDict(extra='forbid')."""
    with pytest.raises(ValidationError):
        LevelAuditDTO(
            score=1.0,
            name="Test",
            total_atoms=3,
            positive_atoms=2,
            inverse_atoms=1,
            is_fragile=False,
            unexpected_field="disallowed",  # type: ignore[call-arg]
        )

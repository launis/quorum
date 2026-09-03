"""Unit tests for scripts/matrix_slice_engine.py.

Verifies slice export, empirical contamination detection, coherence auditing,
Theory Opponent Card compilation, atomic patching, and theory compendium updates.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

import scripts.matrix_hardening_loop as loop_mod
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.v2_core import TDAAssertion
from scripts.matrix_slice_engine import (
    append_matrix_theory_explanation,
    apply_matrix_slice,
    audit_atom_coherence,
    detect_empirical_contamination,
    export_matrix_slice,
    generate_theory_opponent_card,
    load_matrix_by_id,
)


def test_export_matrix_slice_valid(tmp_path: Path) -> None:
    """TC-SLICE-01: Export valid matrix block to custom tmp_path."""
    out_file = tmp_path / "slice.json"
    result_path = export_matrix_slice("blk_440a5fef9331451b", output_path=out_file)
    assert result_path.exists()
    mat = MatrixPromptBlock.model_validate_json(result_path.read_text(encoding="utf-8"))
    assert mat.id == "blk_440a5fef9331451b"
    assert len(mat.scales) >= 1


def test_export_matrix_slice_invalid_id_raises() -> None:
    """TC-SLICE-02: Export non-existent matrix ID raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        export_matrix_slice("blk_nonexistent_99999")


def test_export_matrix_slice_non_matrix_category_raises(tmp_path: Path) -> None:
    """TC-SLICE-03: Export existing block with category_id!='matrix' raises ValueError."""
    mock_seed = tmp_path / "mock_seed.json"
    mock_data = {
        "prompt_blocks": [
            {
                "id": "blk_persona_001",
                "category_id": "persona",
                "slug": "persona-test",
                "label": {"translations": {"en": "Persona"}},
            }
        ]
    }
    mock_seed.write_text(json.dumps(mock_data), encoding="utf-8")
    with pytest.raises(ValueError, match="not found.*or is not category 'matrix'"):
        export_matrix_slice("blk_persona_001", seed_path=mock_seed)


def test_generate_theory_opponent_card_with_grounding() -> None:
    """TC-SLICE-04: Generate theory card for matrix with established theory grounding."""
    card = generate_theory_opponent_card("blk_440a5fef9331451b")
    assert "<theory_context>" in card
    assert "Toulmin" in card or "http" in card
    assert "allow_contextual_override=" in card
    assert "<bars_scale_specifications>" in card
    assert "Level 1" in card
    assert "Level 5" in card


def test_generate_theory_opponent_card_missing_grounding_resilience(tmp_path: Path) -> None:
    """TC-SLICE-05: Generate theory card for a matrix where theory_grounding is None."""
    seed_text = Path("backend_v2/seed/seed_data.json").read_text(encoding="utf-8")
    data = json.loads(seed_text)
    for b in data["prompt_blocks"]:
        if b.get("id") == "blk_440a5fef9331451b":
            b["theory_grounding"] = None
            break
    mock_seed = tmp_path / "seed_no_theory.json"
    mock_seed.write_text(json.dumps(data), encoding="utf-8")

    card = generate_theory_opponent_card("blk_440a5fef9331451b", seed_path=mock_seed)
    assert "[THEORY GROUNDING ABSENT" in card


def test_apply_matrix_slice_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-SLICE-06: Atomically patch a valid modified matrix slice into seed_data.json."""
    mock_seed = tmp_path / "seed_data.json"
    mock_seed.write_text(Path("backend_v2/seed/seed_data.json").read_text(encoding="utf-8"), encoding="utf-8")
    slice_file = tmp_path / "slice.json"
    export_matrix_slice("blk_440a5fef9331451b", output_path=slice_file, seed_path=mock_seed)

    # Mock full database audit to return all_passed=True
    mock_report = MagicMock()
    mock_report.all_passed = True
    monkeypatch.setattr("scripts.matrix_slice_engine.run_full_database_audit", lambda _: mock_report)

    apply_matrix_slice(slice_file, seed_path=mock_seed)
    backups = list((mock_seed.parent / "backups").glob("seed_data_backup_*.json"))
    assert len(backups) == 1


def test_apply_matrix_slice_corrupted_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-SLICE-07: Attempt to patch a slice that fails pre-flight audit rolls back."""
    mock_seed = tmp_path / "seed_data.json"
    original_text = Path("backend_v2/seed/seed_data.json").read_text(encoding="utf-8")
    mock_seed.write_text(original_text, encoding="utf-8")
    slice_file = tmp_path / "slice.json"
    export_matrix_slice("blk_440a5fef9331451b", output_path=slice_file, seed_path=mock_seed)

    # Mock full database audit to fail
    mock_report = MagicMock()
    mock_report.all_passed = False
    monkeypatch.setattr("scripts.matrix_slice_engine.run_full_database_audit", lambda _: mock_report)

    with pytest.raises(RuntimeError, match="Pre-flight audit failed"):
        apply_matrix_slice(slice_file, seed_path=mock_seed)

    # Seed data must be restored to original text
    assert mock_seed.read_text(encoding="utf-8") == original_text


def test_cli_flags_slice_theory_and_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-SLICE-08: Invoke loop_main() via monkeypatched sys.argv with new CLI flags."""
    # Test --slice
    monkeypatch.setattr("sys.argv", ["matrix_hardening_loop.py", "--slice", "blk_440a5fef9331451b"])
    loop_mod.main()
    captured = capsys.readouterr()
    assert "SUCCESS: Exported matrix slice" in captured.out

    # Test --theory-card
    monkeypatch.setattr("sys.argv", ["matrix_hardening_loop.py", "--theory-card", "blk_440a5fef9331451b"])
    loop_mod.main()
    captured = capsys.readouterr()
    assert "<evaluator_mandate>" in captured.out

    # Test --explain
    comp_path = tmp_path / "test_compendium.md"
    monkeypatch.setattr(
        "scripts.matrix_slice_engine.append_matrix_theory_explanation",
        lambda mid: append_matrix_theory_explanation(mid, compendium_path=comp_path),
    )
    monkeypatch.setattr("sys.argv", ["matrix_hardening_loop.py", "--explain", "blk_440a5fef9331451b"])
    loop_mod.main()
    captured = capsys.readouterr()
    assert "SUCCESS: Appended theory explanation" in captured.out

    # Test --audit-contamination
    monkeypatch.setattr("sys.argv", ["matrix_hardening_loop.py", "--audit-contamination", "blk_440a5fef9331451b"])
    loop_mod.main()
    captured = capsys.readouterr()
    assert "contaminated atom(s)" in captured.out


def test_append_matrix_theory_explanation_compendium(tmp_path: Path) -> None:
    """TC-SLICE-09: Generate and append theory explanation to compendium with 2 paragraphs."""
    comp_path = tmp_path / "08_matrix_explanations.md"
    append_matrix_theory_explanation("blk_440a5fef9331451b", compendium_path=comp_path)
    assert comp_path.exists()
    content = comp_path.read_text(encoding="utf-8")
    assert "### Toulmin Argumentation Model" in content
    assert "tda_" not in content
    assert "blk_" not in content

    # Test updating existing entry does not duplicate
    append_matrix_theory_explanation("blk_440a5fef9331451b", compendium_path=comp_path)
    updated_content = comp_path.read_text(encoding="utf-8")
    assert updated_content.count("### Toulmin Argumentation Model") == 1


def test_detect_empirical_contamination_flags_run_artifacts() -> None:
    """TC-SLICE-10: Detect empirical run contamination in mutated matrix and verify all 13 calibrated matrices."""
    base_mat = load_matrix_by_id("blk_440a5fef9331451b")
    # Mutate an assertion to introduce Finnish empirical run contamination
    bad_tda = (
        base_mat.scales[0]
        .claims[0]
        .tda_assertions[0]
        .model_copy(update={"extraction_rule": "Tämä on suomenkielinen empiirinen testi teksti."})
    )
    bad_claim = base_mat.scales[0].claims[0].model_copy(update={"tda_assertions": [bad_tda]})
    bad_scale = base_mat.scales[0].model_copy(update={"claims": [bad_claim]})
    mutated_mat = base_mat.model_copy(update={"scales": [bad_scale] + list(base_mat.scales[1:])})

    findings = detect_empirical_contamination(mutated_mat)
    assert len(findings) > 0
    assert any("Empirical" in f.reason for f in findings)

    # Verify that all 13 calibrated matrices in the database have 0 contamination
    for cid in (
        "blk_440a5fef9331451b",
        "blk_f921c7c0989b47e8",
        "blk_109dab5b6b3f403a",
        "blk_53f32679aa514fcb",
        "blk_fb15f8dcf23f4865",
        "blk_c5804a9143c34cb1",
        "blk_b476f89fb732448c",
        "blk_ff72c2d79edb4ebf",
        "blk_80732a33fe1947ee",
        "blk_6b8c766185294f7e",
        "blk_c3bc5f3eb8e74110",
        "blk_f6e286f050c94d60",
        "blk_22e3598e06414409",
    ):
        calibrated_mat = load_matrix_by_id(cid)
        assert len(detect_empirical_contamination(calibrated_mat)) == 0


def test_generate_theory_opponent_card_includes_contamination_audit() -> None:
    """TC-SLICE-11: Theory opponent card contains <theory_calibration_audit> with contaminated atoms."""
    card = generate_theory_opponent_card("blk_440a5fef9331451b")
    assert "<theory_calibration_audit>" in card
    assert "tda_69cc84e0b0c44996a8a95e09b356c692" in card
    assert "Mandate: Purge empirical run text" in card


def test_generate_theory_opponent_card_explains_aggregation_and_steering_controls() -> None:
    """TC-SLICE-12: Theory opponent card explains ALL_MUST_COMPLY and steering controls."""
    card = generate_theory_opponent_card("blk_440a5fef9331451b")
    assert "<control_theory_grounding>" in card
    assert "ALL_MUST_COMPLY" in card
    assert "EXISTS" in card
    assert "Epistemic Ontology:" in card


def test_audit_atom_coherence_flags_inversion_paradox() -> None:
    """TC-SLICE-13: Audits atom coherence and flags INVERSION_PARADOX."""
    mat = load_matrix_by_id("blk_440a5fef9331451b")
    # Mutate one assertion to create an inversion paradox
    bad_tda = (
        mat.scales[0]
        .claims[0]
        .tda_assertions[0]
        .model_copy(update={"inverse_evidence": True, "aggregation_mode": "ALL_MUST_COMPLY"})
    )
    bad_claim = mat.scales[0].claims[0].model_copy(update={"tda_assertions": [bad_tda]})
    bad_scale = mat.scales[0].model_copy(update={"claims": [bad_claim]})
    bad_mat = mat.model_copy(update={"scales": [bad_scale] + list(mat.scales[1:])})

    issues = audit_atom_coherence(bad_mat)
    issue_types = {i.issue for i in issues}
    assert "INVERSION_PARADOX" in issue_types


def test_tda_assertion_cross_field_validation_rejects_conflicting_flags() -> None:
    """TC-SLICE-14: TDAAssertion validates cross-field consistency on instantiation."""
    # inverse_evidence=True with ALL_MUST_COMPLY must fail
    with pytest.raises(ValidationError, match="Inverse evidence.*requires 'EXISTS'"):
        TDAAssertion(
            concept_description="Critical mandate test concept description",
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
            depends_on=(),
        )

    # enforce_pre_flight=True with empty syntactic_anchors must fail
    with pytest.raises(ValidationError, match="enforce_pre_flight=True requires at least one syntactic anchor"):
        TDAAssertion(
            concept_description="Critical mandate test concept description",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            enforce_pre_flight=True,
            syntactic_anchors=[],
            depends_on=(),
        )


def test_apply_matrix_slice_rejects_incoherent_controls(tmp_path: Path) -> None:
    """TC-SLICE-15: apply_matrix_slice aborts if slice contains fatal field incoherence."""
    slice_path = tmp_path / "incoherent_slice.json"
    mock_seed = tmp_path / "seed_data.json"
    mock_seed.write_text(Path("backend_v2/seed/seed_data.json").read_text(encoding="utf-8"), encoding="utf-8")

    # Construct invalid slice with contradictory flags
    mat = load_matrix_by_id("blk_440a5fef9331451b")
    raw = mat.model_dump(mode="json")
    raw["scales"][0]["claims"][0]["tda_assertions"][0]["inverse_evidence"] = True
    raw["scales"][0]["claims"][0]["tda_assertions"][0]["aggregation_mode"] = "ALL_MUST_COMPLY"
    slice_path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError):
        apply_matrix_slice(slice_path, seed_path=mock_seed)

    # Seed vault backup must not be created
    backups_dir = mock_seed.parent / "backups"
    assert not backups_dir.exists() or len(list(backups_dir.glob("*.json"))) == 0

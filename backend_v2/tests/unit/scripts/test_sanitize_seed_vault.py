"""Unit tests for the Seed Vault Sanitizer CLI tool (scripts/sanitize_seed_vault.py)."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import PromptBlockCategory
from scripts.sanitize_seed_vault import (
    SanitizeResult,
    atomic_save_seed_data,
    clean_mechanical_phrases,
    create_vault_backup,
    main,
    run_seed_vault_sanitization,
    sanitize_prompt_blocks,
    strip_raw_xml,
)


def _create_raw_matrix_block() -> dict[str, object]:
    """Helper to create a raw matrix block dictionary with mechanical phrases and raw XML."""
    return {
        "id": "blk_1234567890abcdef",
        "slug": "test_matrix",
        "category_id": PromptBlockCategory.MATRIX.value,
        "label": {"translations": {"en": "Test Matrix", "fi": "Testimatriisi"}},
        "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
        "ai_description": "<system_directive>Raw XML description</system_directive>",
        "scales": [
            {
                "score": 1,
                "ai_label": "Low",
                "claims": [
                    {
                        "label": {"translations": {"en": "Sample claim", "fi": "Esimerkkiväite"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_453ddf8b14a442e988836098e3c7b55c",
                                "concept_description": "ABSOLUTE MITIGATION ENFORCEMENT: The risk is identified but no physical action verb follows.",
                                "extraction_rule": "ABSOLUTE MITIGATION ENFORCEMENT: Locate and verify if risk is unmitigated.",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            },
                            {
                                "tda_id": "tda_11112222333344445555666677778888",
                                "concept_description": "<directive>A generic concept</directive> with IF AND ONLY IF count is EXACTLY ZERO.",
                                "extraction_rule": "Extract IF AND ONLY IF count of markers is EXACTLY ZERO.",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            },
                        ],
                    }
                ],
            }
        ],
    }


def test_sanitize_dto_structure() -> None:
    """Test SanitizeResult structure, strictness, and default values."""
    res = SanitizeResult()
    assert res.total_blocks_sanitized == 0
    assert res.total_atoms_mutated == 0
    assert res.is_dry_run is False
    assert res.success is True

    # Strict extra forbid validation
    with pytest.raises(ValidationError):
        SanitizeResult.model_validate({"unknown_field": True})


def test_strip_raw_xml() -> None:
    """Test that XML tags and angle brackets are cleanly stripped."""
    assert strip_raw_xml("<directive>Hello World</directive>") == "Hello World"
    assert strip_raw_xml("Plain text without tags") == "Plain text without tags"
    assert strip_raw_xml("<rule name='test'>Value</rule>") == "Value"
    assert strip_raw_xml("<>Loose brackets<>") == "Loose brackets"


def test_clean_mechanical_phrases() -> None:
    """Test that mechanical imperatives and counting artifacts are sanitized."""
    raw = "ABSOLUTE MITIGATION ENFORCEMENT: Extract IF AND ONLY IF count of first-person markers is EXACTLY ZERO."
    cleaned = clean_mechanical_phrases(raw)
    assert "ABSOLUTE MITIGATION ENFORCEMENT" not in cleaned
    assert "IF AND ONLY IF" not in cleaned
    assert "EXACTLY ZERO" not in cleaned
    assert "markers are absent" in cleaned


def test_create_vault_backup(tmp_path: Path) -> None:
    """Test that timestamped backup copies are saved to the backups/ subdirectory."""
    seed_file = tmp_path / "seed_data.json"
    seed_file.write_text(json.dumps({"test": 123}), encoding="utf-8")

    backup_path = create_vault_backup(seed_file)
    assert backup_path.exists()
    assert backup_path.parent == tmp_path / "backups"
    assert backup_path.name.startswith("seed_data_backup_")
    assert json.loads(backup_path.read_text(encoding="utf-8")) == {"test": 123}


def test_atomic_save_seed_data(tmp_path: Path) -> None:
    """Test atomic file persistence with json dry-run validation."""
    target_file = tmp_path / "seed_data.json"
    data = {"prompt_blocks": [], "steps": [], "workflows": [], "output_profiles": []}

    atomic_save_seed_data(data, target_file)
    assert target_file.exists()
    assert json.loads(target_file.read_text(encoding="utf-8")) == data


def test_sanitize_prompt_blocks_pipeline() -> None:
    """Test that prompt blocks and atoms are cleanly transformed and validated."""
    raw_block = _create_raw_matrix_block()
    sanitized_blocks, mutated_count = sanitize_prompt_blocks([raw_block])

    assert len(sanitized_blocks) == 1
    assert mutated_count == 2

    block = sanitized_blocks[0]
    assert "<system_directive>" not in str(block["ai_description"])

    assertions = block["scales"][0]["claims"][0]["tda_assertions"]  # type: ignore[index]
    # Check specific atom harmonization
    a1 = assertions[0]
    assert a1["tda_id"] == "tda_453ddf8b14a442e988836098e3c7b55c"
    assert "ABSOLUTE MITIGATION ENFORCEMENT" not in a1["concept_description"]
    assert "Identified organizational or operational risks" in a1["concept_description"]

    # Check generic atom sanitization
    a2 = assertions[1]
    assert "<directive>" not in a2["concept_description"]
    assert "EXACTLY ZERO" not in a2["concept_description"]
    assert "EXACTLY ZERO" not in a2["extraction_rule"]


def test_run_seed_vault_sanitization(tmp_path: Path) -> None:
    """Test full sanitization runner with and without dry-run."""
    seed_file = tmp_path / "seed_data.json"
    data = {
        "prompt_blocks": [_create_raw_matrix_block()],
        "steps": [],
        "workflows": [],
        "output_profiles": [],
    }
    seed_file.write_text(json.dumps(data), encoding="utf-8")

    # 1. Dry run
    dry_res = run_seed_vault_sanitization(seed_file, dry_run=True)
    assert dry_res.is_dry_run is True
    assert dry_res.backup_path is None
    assert dry_res.total_blocks_sanitized == 1

    # 2. Live run
    live_res = run_seed_vault_sanitization(seed_file, dry_run=False)
    assert live_res.is_dry_run is False
    assert live_res.backup_path is not None
    assert live_res.total_blocks_sanitized == 1

    # Verify persisted content
    persisted = json.loads(seed_file.read_text(encoding="utf-8"))
    assert len(persisted["prompt_blocks"]) == 1
    assert "<system_directive>" not in persisted["prompt_blocks"][0]["ai_description"]


def test_sanitize_cli_exit_codes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI main() behavior with --dry-run and file path arguments."""
    seed_file = tmp_path / "seed_data.json"
    data = {
        "prompt_blocks": [_create_raw_matrix_block()],
        "steps": [],
        "workflows": [],
        "output_profiles": [],
    }
    seed_file.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["sanitize_seed_vault.py", "--seed-path", str(seed_file), "--dry-run"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_sanitize_cli_subprocesses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI main() with --test and --reseed flags using subprocess mocks."""
    seed_file = tmp_path / "seed_data.json"
    data = {
        "prompt_blocks": [_create_raw_matrix_block()],
        "steps": [],
        "workflows": [],
        "output_profiles": [],
    }
    seed_file.write_text(json.dumps(data), encoding="utf-8")

    class MockProc:
        returncode = 0

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockProc())
    monkeypatch.setattr(
        "sys.argv",
        ["sanitize_seed_vault.py", "--seed-path", str(seed_file), "--test", "--reseed"],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_sanitize_full_seed_vault_dry_run() -> None:
    """Test executing sanitization pipeline on the real seed_data.json in dry-run mode."""
    real_seed = Path("backend_v2/seed/seed_data.json")
    assert real_seed.exists(), "Master seed_data.json must exist."

    result = run_seed_vault_sanitization(real_seed, dry_run=True)
    assert result.success is True
    assert result.is_dry_run is True
    assert result.total_blocks_sanitized >= 90
    assert result.total_steps_sanitized >= 19
    assert result.total_workflows_sanitized >= 1
    assert result.total_profiles_sanitized >= 1


def test_sanitize_zero_reflection() -> None:
    """Uses Python AST parser to verify zero getattr/hasattr/setattr calls in sanitize_seed_vault.py."""
    target_script = Path("scripts/sanitize_seed_vault.py")
    assert target_script.exists(), "sanitize_seed_vault.py script must exist."

    tree = ast.parse(target_script.read_text(encoding="utf-8"), filename=str(target_script))

    banned_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr", "setattr"):
                banned_calls.append(node.func.id)

    assert len(banned_calls) == 0, f"Found reflection calls {banned_calls} in sanitize_seed_vault.py."

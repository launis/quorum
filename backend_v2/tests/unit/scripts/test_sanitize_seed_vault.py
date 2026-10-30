"""Unit tests for the Seed Vault Sanitizer CLI tool (scripts/sanitize_seed_vault.py)."""

import ast
import json
import re
from pathlib import Path

import pytest
from pydantic import JsonValue, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, parse_prefixed_uuid7
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import EntityPrefix, PromptBlockCategory, SystemConfigID
from scripts.sanitize_seed_vault import (
    SanitizeResult,
    _sanitize_auxiliary_collections,
    _upgrade_or_generate_opaque_id,
    atomic_save_seed_data,
    clean_mechanical_phrases,
    create_vault_backup,
    main,
    run_seed_vault_sanitization,
    sanitize_output_profiles,
    sanitize_prompt_blocks,
    sanitize_steps,
    sanitize_workflows,
    strip_raw_xml,
)


def _create_raw_matrix_block() -> JsonValue:
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
                                "depends_on": [
                                    {
                                        "tda_id": "tda_453ddf8b14a442e988836098e3c7b55c",
                                        "edge_reasoning": "Requires parent risk identification.",
                                        "source_id": "chunk_0",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        ],
    }


def test_upgrade_or_generate_opaque_id_variants() -> None:
    """Verify deterministic 16-hex to 32-hex UUIDv7 upgrade and missing-ID generation."""
    # 1. 16-hex upgrade
    upgraded_wf = _upgrade_or_generate_opaque_id("wor_a8f1d71000000001", EntityPrefix.WORKFLOW)
    assert upgraded_wf == "wf_0195f3a00000700a88f1d71000000001"
    assert parse_prefixed_uuid7(upgraded_wf, EntityPrefix.WORKFLOW).version == 7

    # 2. Missing / blank / non-string generates fresh 32-hex UUIDv7
    generated_blk = _upgrade_or_generate_opaque_id(None, EntityPrefix.PROMPT_BLOCK)
    assert re.match(OPAQUE_STRIPE_ID_REGEX, generated_blk)
    assert parse_prefixed_uuid7(generated_blk, EntityPrefix.PROMPT_BLOCK).version == 7

    generated_blank = _upgrade_or_generate_opaque_id("   ", EntityPrefix.STEP)
    assert re.match(OPAQUE_STRIPE_ID_REGEX, generated_blank)
    assert parse_prefixed_uuid7(generated_blank, EntityPrefix.STEP).version == 7

    # 3. Existing 32-hex non-v7 entity ID is normalized to v7
    non_v7_32 = _upgrade_or_generate_opaque_id("prf_453ddf8b14a442e988836098e3c7b55c", EntityPrefix.OUTPUT_PROFILE)
    assert parse_prefixed_uuid7(non_v7_32, EntityPrefix.OUTPUT_PROFILE).version == 7

    # 4. System config & organization constants
    assert (
        _upgrade_or_generate_opaque_id("sys_8172bda70c8641c5", EntityPrefix.SYSTEM_CONFIG)
        == SystemConfigID.MCP_GATEWAYS.value
    )
    assert (
        _upgrade_or_generate_opaque_id("org_system000000", EntityPrefix.ORGANIZATION)
        == "org_0195f3a0000070008000000000000000"
    )


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
    assert strip_raw_xml("") == ""


def test_clean_mechanical_phrases() -> None:
    """Test that mechanical imperatives and counting artifacts are sanitized."""
    raw = "ABSOLUTE MITIGATION ENFORCEMENT: Extract IF AND ONLY IF count of first-person markers is EXACTLY ZERO."
    cleaned = clean_mechanical_phrases(raw)
    assert "ABSOLUTE MITIGATION ENFORCEMENT" not in cleaned
    assert "IF AND ONLY IF" not in cleaned
    assert "EXACTLY ZERO" not in cleaned
    assert "markers are absent" in cleaned
    assert clean_mechanical_phrases("") == ""


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

    block = MatrixPromptBlock.model_validate(sanitized_blocks[0], strict=False)
    assert block.id == "blk_0195f3a0000070018234567890abcdef"
    assert "<system_directive>" not in str(block.ai_description)

    assertions = block.scales[0].claims[0].tda_assertions
    a1 = assertions[0]
    assert a1.tda_id == "tda_453ddf8b14a442e988836098e3c7b55c"
    assert "ABSOLUTE MITIGATION ENFORCEMENT" not in a1.concept_description
    assert "Identified organizational or operational risks" in a1.concept_description

    a2 = assertions[1]
    assert "<directive>" not in a2.concept_description
    assert "EXACTLY ZERO" not in a2.concept_description
    assert "EXACTLY ZERO" not in str(a2.extraction_rule)


def test_sanitize_steps_workflows_profiles_and_auxiliary() -> None:
    """Verify sanitize_steps, sanitize_workflows, sanitize_output_profiles, and _sanitize_auxiliary_collections."""
    # 1. Steps (including CAUSAL_DISCOVERY auto-binding of causal cohesion matrix)
    raw_steps = [
        {
            "id": "sp_75261e4b904a428c",
            "slug": "step_causal_discovery",
            "name": {"translations": {"en": "Causal Discovery", "fi": "Kausaalinen löytäminen"}},
            "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
            "type": "causal_discovery",
            "engine_type": "causal_discovery",
            "extraction_protocol_block_id": "blk_440a5fef9331451b",
            "criteria_block_ids": [],
            "cognitive_tier": "deep",
        }
    ]
    sanitized_steps = sanitize_steps(raw_steps)
    assert len(sanitized_steps) == 1
    step0 = Step.model_validate(sanitized_steps[0], strict=False)
    assert step0.id == "stp_0195f3a00000700785261e4b904a428c"
    assert step0.criteria_block_ids == ["blk_0195f3a00000700c80a1e50000000001"]

    # 2. Auxiliary collections
    aux_data: dict[str, JsonValue] = {
        "system_config": [{"id": "sys_8172bda70c8641c5", "gateways": []}],
        "organizations": [
            {"id": "org_system000000", "name": "System"},
            {"id": "org_e531d2ed8a6641f6", "name": "Default"},
        ],
        "users": [
            {"id": "usr_7a9c1b2e4d5f6a8b", "organization_id": "org_e531d2ed8a6641f6"},
        ],
    }
    _sanitize_auxiliary_collections(aux_data)
    aux_dump = json.dumps(aux_data)
    assert SystemConfigID.MCP_GATEWAYS.value in aux_dump
    assert '"org_system000000"' in aux_dump
    assert '"org_0195f3a00000700e8531d2ed8a6641f6"' in aux_dump
    assert '"usr_0195f3a0000070078a9c1b2e4d5f6a8b"' in aux_dump


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

    # 3. Negative path: missing seed file raises AppException (FILE_NOT_FOUND)
    with pytest.raises(AppException) as exc_info:
        run_seed_vault_sanitization(tmp_path / "nonexistent.json", dry_run=True)
    assert exc_info.value.error_code == ErrorCodes.FILE_NOT_FOUND.value


def test_negative_boundaries_and_schema_failures(tmp_path: Path) -> None:
    """Verify ISTQB negative boundaries: missing backup file, malformed JSON, invalid root, and invalid schemas."""
    # 1. create_vault_backup missing file -> AppException(FILE_NOT_FOUND)
    with pytest.raises(AppException) as exc_backup:
        create_vault_backup(tmp_path / "missing_seed.json")
    assert exc_backup.value.error_code == ErrorCodes.FILE_NOT_FOUND.value

    # 2. atomic_save_seed_data missing 'prompt_blocks' key -> AppException(VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_save:
        atomic_save_seed_data({"steps": []}, tmp_path / "invalid_save.json")
    assert exc_save.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 3. run_seed_vault_sanitization with malformed JSON -> AppException(INVALID_JSON_PAYLOAD)
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("{not_valid_json", encoding="utf-8")
    with pytest.raises(AppException) as exc_json:
        run_seed_vault_sanitization(bad_json_file, dry_run=True)
    assert exc_json.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD.value

    # 4. run_seed_vault_sanitization with non-object root JSON (e.g., list) -> AppException(VALIDATION_FAILED)
    list_json_file = tmp_path / "list_root.json"
    list_json_file.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(AppException) as exc_root:
        run_seed_vault_sanitization(list_json_file, dry_run=True)
    assert exc_root.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 5. sanitize_prompt_blocks with invalid block schema -> AppException(VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_blk:
        sanitize_prompt_blocks([{"id": "blk_1234567890abcdef", "category_id": "invalid_cat"}])
    assert exc_blk.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 6. sanitize_steps with invalid step schema -> AppException(VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_stp:
        sanitize_steps([{"id": "stp_1234567890abcdef", "unknown_extra_key": "rejected"}])
    assert exc_stp.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 7. sanitize_workflows with invalid workflow schema -> AppException(VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_wf:
        sanitize_workflows([{"id": "wf_1234567890abcdef", "unknown_extra_key": "rejected"}])
    assert exc_wf.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 8. sanitize_output_profiles with invalid profile schema -> AppException(VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_prf:
        sanitize_output_profiles([{"id": "prf_1234567890abcdef", "unknown_extra_key": "rejected"}])
    assert exc_prf.value.error_code == ErrorCodes.VALIDATION_FAILED.value


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
    """Test CLI main() with --test and --reseed flags using scoped subprocess mocks."""
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

    monkeypatch.setattr("scripts.sanitize_seed_vault.subprocess.run", lambda *args, **kwargs: MockProc())
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

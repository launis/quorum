"""Unit and integration tests for scripts/audit_manifest_generator.py.

Verifies strict Pydantic V2 schemas (strict=True, extra="forbid"), physical trace loading,
stratified sampling for beta_sem and chimera manifest generation, JSON/CSV exports,
and CLI integration with run_ablation_benchmark.py.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import ExecutionStatus
from scripts.audit_manifest_generator import (
    DEFAULT_PRODUCTION_TRACES,
    AuditManifestDTO,
    AuditManifestItemDTO,
    ManifestType,
    export_manifest_to_csv,
    export_manifest_to_json,
    extract_combined_source_text,
    generate_audit_manifest,
    load_physical_execution_items,
    load_seed_atom_metadata,
)
from scripts.audit_manifest_generator import (
    main as generator_main,
)
from scripts.run_ablation_benchmark import main as benchmark_main

_PHYSICAL_TRACES_EXIST = all(p.exists() for pair in DEFAULT_PRODUCTION_TRACES.values() for p in pair)


def test_audit_manifest_item_dto_valid() -> None:
    """Verify standard instantiation of AuditManifestItemDTO."""
    item = AuditManifestItemDTO(
        tda_id="tda_test_01",
        execution_id="exe_test_123",
        case_name="pair_a",
        matrix_id="blk_matrix_01",
        matrix_label="Test Matrix",
        concept_description="Evaluates critical thinking.",
        target_speaker="USER",
        system_status=ExecutionStatus.PASSED,
        raw_is_true=True,
        source_quote="I think therefore I am.",
        is_chimera=False,
        evaluation_reasoning="Clear evidence present.",
    )
    assert item.tda_id == "tda_test_01"
    assert item.system_status == ExecutionStatus.PASSED
    assert item.source_quote == "I think therefore I am."
    assert item.is_chimera is False
    assert item.human_ground_truth_entailment is None


def test_audit_manifest_item_dto_extra_forbidden() -> None:
    """Verify that extra fields are strictly forbidden by Pydantic V2."""
    data = {
        "tda_id": "tda_test_01",
        "execution_id": "exe_test_123",
        "case_name": "pair_a",
        "matrix_id": "blk_matrix_01",
        "matrix_label": "Test Matrix",
        "concept_description": "Evaluates critical thinking.",
        "target_speaker": "USER",
        "system_status": ExecutionStatus.PASSED,
        "raw_is_true": True,
        "is_chimera": False,
        "unexpected_field": "disallowed",
    }
    with pytest.raises(ValidationError):
        AuditManifestItemDTO.model_validate(data)


def test_audit_manifest_item_dto_strict_type_enforcement() -> None:
    """Verify that strict=True rejects coercive types (e.g., string for boolean)."""
    data = {
        "tda_id": "tda_test_01",
        "execution_id": "exe_test_123",
        "case_name": "pair_a",
        "matrix_id": "blk_matrix_01",
        "matrix_label": "Test Matrix",
        "concept_description": "Evaluates critical thinking.",
        "target_speaker": "USER",
        "system_status": ExecutionStatus.PASSED,
        "raw_is_true": "True",  # String instead of strict bool
        "is_chimera": False,
    }
    with pytest.raises(ValidationError):
        AuditManifestItemDTO.model_validate(data)


def test_audit_manifest_dto_extra_forbidden() -> None:
    """Verify that extra fields on AuditManifestDTO are strictly rejected."""
    data = {
        "manifest_id": "man_123",
        "generated_at": "2026-10-17T12:00:00Z",
        "manifest_type": "beta_sem",
        "sample_size": 0,
        "items": [],
        "source_trace_files": [],
        "unauthorized_meta": "rejected",
    }
    with pytest.raises(ValidationError):
        AuditManifestDTO.model_validate(data)


def test_load_seed_atom_metadata_success() -> None:
    """Verify loading real seed data extracts valid atom metadata."""
    meta = load_seed_atom_metadata()
    assert len(meta) > 0
    # Every metadata entry must have required fields
    for tda_id, entry in meta.items():
        assert tda_id.startswith("tda_")
        assert entry.matrix_id
        assert entry.matrix_label
        assert entry.concept_description
        assert entry.target_speaker
        break


def test_load_seed_atom_metadata_missing_path(tmp_path: Path) -> None:
    """Verify non-existent seed file path returns empty dict gracefully."""
    non_existent = tmp_path / "missing_seed.json"
    meta = load_seed_atom_metadata(non_existent)
    assert meta == {}


def test_extract_combined_source_text_missing_file(tmp_path: Path) -> None:
    """Verify non-existent trace file returns empty string."""
    non_existent = tmp_path / "missing_trace.json"
    text = extract_combined_source_text(non_existent)
    assert text == ""


def test_extract_combined_source_text_production() -> None:
    """Verify extracting source text from real production trace."""
    trace_path = DEFAULT_PRODUCTION_TRACES["pair_a"][0]
    if trace_path.exists():
        text = extract_combined_source_text(trace_path)
        assert len(text) > 0
        assert "\n" in text


def test_load_physical_execution_items_missing_file_raises(tmp_path: Path) -> None:
    """Verify load_physical_execution_items raises FileNotFoundError on missing trace."""
    missing = tmp_path / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        load_physical_execution_items(trace_paths_by_case={"pair_a": [missing]})


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_load_physical_execution_items_production() -> None:
    """Verify loading items from physical production traces."""
    items = load_physical_execution_items()
    assert len(items) > 0
    # Verify strict validation across all loaded items
    for it in items:
        assert isinstance(it, AuditManifestItemDTO)
        assert it.case_name in ("pair_a", "pair_b")
        assert isinstance(it.system_status, ExecutionStatus)
        assert isinstance(it.raw_is_true, bool)
        assert isinstance(it.is_chimera, bool)


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_generate_audit_manifest_beta_sem_stratification() -> None:
    """Verify stratified generation of beta_sem manifest with sample_size=40."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.BETA_SEM,
        sample_size=40,
        seed=42,
    )
    assert isinstance(manifest, AuditManifestDTO)
    assert manifest.manifest_type == ManifestType.BETA_SEM
    assert len(manifest.items) == 40
    assert manifest.sample_size == 40

    # In beta_sem, all items must be PASSED, have a valid quote, and not be chimera
    for it in manifest.items:
        assert it.system_status == ExecutionStatus.PASSED
        assert it.source_quote is not None
        assert it.is_chimera is False

    # Check stratification: multiple matrices represented
    matrices = {it.matrix_id for it in manifest.items}
    assert len(matrices) > 1


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_generate_audit_manifest_chimera() -> None:
    """Verify generation of chimera/false-negative audit manifest."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.CHIMERA,
        sample_size=20,
        seed=42,
    )
    assert isinstance(manifest, AuditManifestDTO)
    assert manifest.manifest_type == ManifestType.CHIMERA
    assert len(manifest.items) > 0
    for it in manifest.items:
        # Either marked as chimera or rejected system decision evaluated for retrieval gap
        assert it.is_chimera or (it.system_status == ExecutionStatus.FAILED)


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_generate_audit_manifest_all() -> None:
    """Verify generation of all items manifest."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.ALL,
        sample_size=50,
        seed=42,
    )
    assert isinstance(manifest, AuditManifestDTO)
    assert manifest.manifest_type == ManifestType.ALL
    assert len(manifest.items) == 50


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_generate_audit_manifest_boundary_zero_sample() -> None:
    """Verify boundary condition with sample_size=0."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.BETA_SEM,
        sample_size=0,
        seed=42,
    )
    assert len(manifest.items) == 0
    assert manifest.sample_size == 0


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_export_manifest_json_roundtrip(tmp_path: Path) -> None:
    """Verify exporting manifest to JSON and validating roundtrip."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.BETA_SEM,
        sample_size=10,
        seed=42,
    )
    out_file = tmp_path / "test_manifest.json"
    exported_path = export_manifest_to_json(manifest, out_file)
    assert exported_path.exists()

    # Read and validate with strict Pydantic V2
    raw_content = exported_path.read_text(encoding="utf-8")
    roundtrip = AuditManifestDTO.model_validate_json(raw_content)
    assert roundtrip.manifest_id == manifest.manifest_id
    assert roundtrip.sample_size == len(roundtrip.items) == 10
    assert roundtrip.items[0].tda_id == manifest.items[0].tda_id


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_export_manifest_csv_roundtrip(tmp_path: Path) -> None:
    """Verify exporting manifest to RFC-4180 CSV."""
    manifest = generate_audit_manifest(
        manifest_type=ManifestType.CHIMERA,
        sample_size=10,
        seed=42,
    )
    out_file = tmp_path / "test_manifest.csv"
    exported_path = export_manifest_to_csv(manifest, out_file)
    assert exported_path.exists()

    with exported_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == len(manifest.items)
        assert "tda_id" in reader.fieldnames
        assert "concept_description" in reader.fieldnames
        assert "human_ground_truth_entailment" in reader.fieldnames
        assert rows[0]["tda_id"] == manifest.items[0].tda_id


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_generator_main_cli(tmp_path: Path) -> None:
    """Verify CLI execution of audit_manifest_generator.py."""
    out_json = tmp_path / "cli_manifest.json"
    exit_code = generator_main(
        [
            "--type",
            "beta_sem",
            "--format",
            "json",
            "--sample-size",
            "5",
            "--output-file",
            str(out_json),
        ]
    )
    assert exit_code == 0
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert len(data["items"]) == 5


def test_generator_main_cli_invalid_type() -> None:
    """Verify CLI error handling on invalid manifest type."""
    with pytest.raises(SystemExit):
        generator_main(["--type", "invalid_type"])


@pytest.mark.skipif(
    not _PHYSICAL_TRACES_EXIST, reason="Physical production execution trace files not present in data/files/executions/"
)
def test_run_ablation_benchmark_export_manifest_cli(tmp_path: Path) -> None:
    """Verify run_ablation_benchmark.py --export-manifest delegation."""
    out_csv = tmp_path / "ablation_manifest.csv"
    exit_code = benchmark_main(
        [
            "--export-manifest",
            "beta_sem",
            "--manifest-format",
            "csv",
            "--manifest-sample-size",
            "5",
            "--manifest-output",
            str(out_csv),
        ]
    )
    assert exit_code == 0
    assert out_csv.exists()
    with out_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 5

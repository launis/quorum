"""Unit tests for standalone execution storage reconciliation script.

Verifies that scripts/reconcile_storage.py detects orphaned database records
and unindexed physical disk runs, enforcing read-only behavior in --check mode
and performing strict Pydantic V2 validated reconciliation in --fix mode.
"""

import json
from pathlib import Path

import pytest
from tinydb import TinyDB

from backend_v2.models.v2_core import ExecutionRecord
from scripts.reconcile_storage import ReconciliationReport, reconcile_storage


@pytest.fixture
def temp_environment(tmp_path: Path) -> tuple[Path, Path]:
    """Creates an isolated temporary TinyDB file and execution storage directory.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        tuple containing (db_path, storage_dir).
    """
    db_file = tmp_path / "test_db.json"
    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Initialize empty executions table in TinyDB
    db = TinyDB(str(db_file), encoding="utf-8")
    db.table("executions")
    db.close()

    return db_file, storage_dir


def test_reconcile_storage_check_dry_run_does_not_mutate(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that --check (fix=False) detects desyncs without mutating the database."""
    db_file, storage_dir = temp_environment

    # 1. Populate DB with an orphaned record
    orphaned_id = "exe_ghost1234567890"
    db = TinyDB(str(db_file), encoding="utf-8")
    table = db.table("executions")
    table.insert(
        {
            "id": orphaned_id,
            "workflow_id": "wor_default",
            "target_locale": "en",
            "output_profile_id": "prof_default",
            "execution_trace_storage_path": f"executions/{orphaned_id}/execution_trace.json",
        }
    )
    db.close()

    # 2. Populate Disk with an unindexed execution
    unindexed_id = "exe_disk9876543210"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text(
        json.dumps([{"step_name": "raw_inputs", "event_type": "input", "content": {"language": "fi"}}]),
        encoding="utf-8",
    )
    pdf_file = exe_dir / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy")

    # Act: Run reconciliation in dry-run mode (fix=False)
    report: ReconciliationReport = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=False)

    # Assert: Report correctly identifies anomalies
    assert not report.is_synced
    assert orphaned_id in report.orphaned_db_ids
    assert unindexed_id in report.unindexed_disk_ids
    assert len(report.pruned_db_ids) == 0
    assert len(report.recovered_disk_ids) == 0

    # Verify DB was NOT mutated
    db = TinyDB(str(db_file), encoding="utf-8")
    records = db.table("executions").all()
    db.close()
    assert len(records) == 1
    assert records[0]["id"] == orphaned_id


def test_reconcile_storage_fix_reconstitutes_and_prunes(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that --fix (fix=True) prunes ghost records and hydrates unindexed disk runs."""
    db_file, storage_dir = temp_environment

    # 1. Populate DB with an orphaned record
    orphaned_id = "exe_0a1b2c3d4e5f6a7b"
    db = TinyDB(str(db_file), encoding="utf-8")
    table = db.table("executions")
    table.insert(
        {
            "id": orphaned_id,
            "workflow_id": "wor_default",
            "target_locale": "en",
            "output_profile_id": "prof_default",
            "execution_trace_storage_path": f"executions/{orphaned_id}/execution_trace.json",
        }
    )
    db.close()

    # 2. Populate Disk with an unindexed execution
    unindexed_id = "exe_f0e1d2c3b4a59687"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text(
        json.dumps([{"step_name": "raw_inputs", "event_type": "input", "content": {"language": "en"}}]),
        encoding="utf-8",
    )
    pdf_file = exe_dir / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy")

    # Act: Run reconciliation in fix mode (fix=True)
    report: ReconciliationReport = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=True)

    # Assert: Report confirms reconciliation actions
    assert report.is_synced
    assert orphaned_id in report.pruned_db_ids
    assert unindexed_id in report.recovered_disk_ids

    # Verify DB now contains ONLY the recovered execution
    db = TinyDB(str(db_file), encoding="utf-8")
    records = db.table("executions").all()
    db.close()

    assert len(records) == 1
    recovered_rec = records[0]
    assert recovered_rec["id"] == unindexed_id

    # Verify 100% Pydantic V2 schema validity
    validated = ExecutionRecord.model_validate(recovered_rec, strict=False)
    assert validated.id == unindexed_id
    assert validated.target_locale == "en"


def test_reconcile_storage_when_already_synced(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that synchronized DB and storage results in is_synced=True and zero modifications."""
    db_file, storage_dir = temp_environment

    synced_id = "exe_7890abcdef123456"
    exe_dir = storage_dir / synced_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    db = TinyDB(str(db_file), encoding="utf-8")
    table = db.table("executions")
    table.insert(
        {
            "id": synced_id,
            "workflow_id": "wor_default",
            "target_locale": "fi",
            "output_profile_id": "prof_default",
            "execution_trace_storage_path": f"executions/{synced_id}/execution_trace.json",
        }
    )
    db.close()

    # Act: Check
    report = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=False)

    # Assert
    assert report.is_synced
    assert len(report.orphaned_db_ids) == 0
    assert len(report.unindexed_disk_ids) == 0
    assert len(report.pruned_db_ids) == 0
    assert len(report.recovered_disk_ids) == 0


def test_reconcile_storage_when_db_does_not_exist(tmp_path: Path) -> None:
    """Verifies that non-existent database file returns is_synced=False without crashing."""
    missing_db = tmp_path / "nonexistent.json"
    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)

    report = reconcile_storage(db_path=missing_db, storage_dir=storage_dir, fix=False)
    assert not report.is_synced


def test_reconcile_storage_fix_without_template_record(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that reconciliation succeeds even when DB has zero existing records (no template)."""
    db_file, storage_dir = temp_environment

    # DB is completely empty (no template record)
    unindexed_id = "exe_1122334455667788"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    report = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=True)
    assert report.is_synced
    assert unindexed_id in report.recovered_disk_ids

    db = TinyDB(str(db_file), encoding="utf-8")
    records = db.table("executions").all()
    db.close()
    assert len(records) == 1
    assert records[0]["id"] == unindexed_id


def test_reconcile_storage_main_cli_synced(
    temp_environment: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifies CLI main() execution in --check mode when storage is synchronized."""
    db_file, storage_dir = temp_environment
    from scripts.reconcile_storage import main

    monkeypatch.setattr(
        "sys.argv",
        ["reconcile_storage.py", "--check", "--db-path", str(db_file), "--storage-dir", str(storage_dir)],
    )

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert "SYNCHRONIZED" in captured.out


def test_reconcile_storage_main_cli_desynced_and_fix(
    temp_environment: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifies CLI main() exits with 1 on desync, and exits with 0 after --fix."""
    db_file, storage_dir = temp_environment
    from scripts.reconcile_storage import main

    # Populate unindexed run
    unindexed_id = "exe_aabbccddeeff0011"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    (exe_dir / "execution_trace.json").write_text("[]", encoding="utf-8")

    # 1. Test --check exits with code 1
    monkeypatch.setattr(
        "sys.argv",
        ["reconcile_storage.py", "--check", "--db-path", str(db_file), "--storage-dir", str(storage_dir)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1

    # 2. Test --fix exits with code 0
    monkeypatch.setattr(
        "sys.argv",
        ["reconcile_storage.py", "--fix", "--db-path", str(db_file), "--storage-dir", str(storage_dir)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


"""Unit tests for standalone execution storage reconciliation script.

Verifies that scripts/reconcile_storage.py detects orphaned database records
and unindexed physical disk runs, enforcing read-only behavior in --check mode
and performing strict Pydantic V2 validated reconciliation in --fix mode.
"""

import json
from pathlib import Path

import pytest
from pydantic import JsonValue

from backend_v2.models.domain.execution import ExecutionRecord
from scripts.reconcile_storage import ReconciliationReport, reconcile_storage


def _write_records(db_file: Path, records: list[dict[str, JsonValue]]) -> None:
    """Helper to write execution records to a JSON snapshot file."""
    indexed = {str(idx): rec for idx, rec in enumerate(records, start=1)}
    db_file.write_text(json.dumps({"executions": indexed}, indent=2), encoding="utf-8")


def _read_records(db_file: Path) -> list[ExecutionRecord]:
    """Helper to read validated ExecutionRecord models from a JSON snapshot file."""
    parsed = json.loads(db_file.read_text(encoding="utf-8"))
    raw_items = list(parsed.get("executions", {}).values())
    return [ExecutionRecord.model_validate(item, strict=False) for item in raw_items]


@pytest.fixture
def temp_environment(tmp_path: Path) -> tuple[Path, Path]:
    """Creates an isolated temporary snapshot file and execution storage directory.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        tuple containing (db_path, storage_dir).
    """
    db_file = tmp_path / "test_db.json"
    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)
    _write_records(db_file, [])
    return db_file, storage_dir


def test_reconcile_storage_check_dry_run_does_not_mutate(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that --check (fix=False) detects desyncs without mutating the database."""
    db_file, storage_dir = temp_environment

    orphaned_id = "exe_0195f3a0000070018111222233334444"
    _write_records(
        db_file,
        [
            {
                "id": orphaned_id,
                "workflow_id": "wor_default",
                "target_locale": "en",
                "output_profile_id": "prof_default",
                "execution_trace_storage_path": f"executions/{orphaned_id}/execution_trace.json",
            }
        ],
    )

    unindexed_id = "exe_0195f3a0000070058555666677778888"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text(
        json.dumps([{"step_name": "raw_inputs", "event_type": "input", "content": {"language": "fi"}}]),
        encoding="utf-8",
    )
    pdf_file = exe_dir / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy")

    report: ReconciliationReport = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=False)

    assert not report.is_synced
    assert orphaned_id in report.orphaned_db_ids
    assert unindexed_id in report.unindexed_disk_ids
    assert len(report.pruned_db_ids) == 0
    assert len(report.recovered_disk_ids) == 0

    records = _read_records(db_file)
    assert len(records) == 1
    assert records[0].id == orphaned_id


def test_reconcile_storage_fix_reconstitutes_and_prunes(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that --fix (fix=True) prunes ghost records and hydrates unindexed disk runs."""
    db_file, storage_dir = temp_environment

    orphaned_id = "exe_0195f3a0000070008a1b2c3d4e5f6a7b"
    _write_records(
        db_file,
        [
            {
                "id": orphaned_id,
                "workflow_id": "wor_default",
                "target_locale": "en",
                "output_profile_id": "prof_default",
                "execution_trace_storage_path": f"executions/{orphaned_id}/execution_trace.json",
            }
        ],
    )

    unindexed_id = "exe_0195f3a00000700f80e1d2c3b4a59687"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text(
        json.dumps([{"step_name": "raw_inputs", "event_type": "input", "content": {"language": "en"}}]),
        encoding="utf-8",
    )
    pdf_file = exe_dir / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy")

    report: ReconciliationReport = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=True)

    assert report.is_synced
    assert orphaned_id in report.pruned_db_ids
    assert unindexed_id in report.recovered_disk_ids

    records = _read_records(db_file)
    assert len(records) == 1
    recovered_rec = records[0]
    assert recovered_rec.id == unindexed_id
    assert recovered_rec.target_locale == "en"


def test_reconcile_storage_when_already_synced(
    temp_environment: tuple[Path, Path],
) -> None:
    """Verifies that synchronized DB and storage results in is_synced=True and zero modifications."""
    db_file, storage_dir = temp_environment

    synced_id = "exe_0195f3a0000070078890abcdef123456"
    exe_dir = storage_dir / synced_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    _write_records(
        db_file,
        [
            {
                "id": synced_id,
                "workflow_id": "wor_default",
                "target_locale": "fi",
                "output_profile_id": "prof_default",
                "execution_trace_storage_path": f"executions/{synced_id}/execution_trace.json",
            }
        ],
    )

    report = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=False)

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

    unindexed_id = "exe_0195f3a0000070018122334455667788"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    report = reconcile_storage(db_path=db_file, storage_dir=storage_dir, fix=True)
    assert report.is_synced
    assert unindexed_id in report.recovered_disk_ids

    records = _read_records(db_file)
    assert len(records) == 1
    assert records[0].id == unindexed_id


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

    unindexed_id = "exe_0195f3a00000700a8abbccddeeff0011"
    exe_dir = storage_dir / unindexed_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    (exe_dir / "execution_trace.json").write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["reconcile_storage.py", "--check", "--db-path", str(db_file), "--storage-dir", str(storage_dir)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1

    monkeypatch.setattr(
        "sys.argv",
        ["reconcile_storage.py", "--fix", "--db-path", str(db_file), "--storage-dir", str(storage_dir)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_extract_trace_metadata_event_workflow_id_and_default_path(tmp_path: Path) -> None:
    """Verify trace event workflow_id extraction and default disk path resolution."""
    from scripts.reconcile_storage import _extract_trace_metadata, _resolve_trace_path

    storage_dir = tmp_path / "executions"
    exe_id = "exe_0195f3a0000070098999888877776666"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text(
        json.dumps([{"step_name": "init", "event_type": "system", "content": {"workflow_id": "wor_event_extracted"}}]),
        encoding="utf-8",
    )

    wf_id, locale = _extract_trace_metadata(trace_file)
    assert wf_id == "wor_event_extracted"
    assert locale == "en"
    assert _resolve_trace_path(storage_dir, exe_id, "nonexistent/path.json") == trace_file


def test_extract_trace_metadata_corrupted(tmp_path: Path) -> None:
    """Ensure invalid JSON in trace file falls back safely to default metadata."""
    from scripts.reconcile_storage import _extract_trace_metadata

    bad_trace = tmp_path / "bad_trace.json"
    bad_trace.write_text("{not-valid-json", encoding="utf-8")

    wf_id, locale = _extract_trace_metadata(bad_trace)
    assert wf_id == "wor_default"
    assert locale == "en"


def test_resolve_trace_path_variations(tmp_path: Path) -> None:
    """Test resolution of direct trace paths and parent-relative paths."""
    from scripts.reconcile_storage import _resolve_trace_path

    storage_dir = tmp_path / "files" / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)

    direct_trace = tmp_path / "custom_trace.json"
    direct_trace.write_text("[]", encoding="utf-8")
    assert _resolve_trace_path(storage_dir, "exe_123", str(direct_trace)) == direct_trace

    rel_path = "executions/exe_rel/execution_trace.json"
    full_rel = storage_dir.parent / rel_path
    full_rel.parent.mkdir(parents=True, exist_ok=True)
    full_rel.write_text("[]", encoding="utf-8")
    assert _resolve_trace_path(storage_dir, "exe_rel", rel_path) == full_rel


def test_extract_trace_metadata_forensic_summary_and_reports(tmp_path: Path) -> None:
    """Test extracting workflow_id, profile_id, and Finnish locale from summary and reports."""
    from scripts.reconcile_storage import _extract_profile_id, _extract_trace_metadata

    exe_dir = tmp_path / "artifacts" / "executions" / "exe_0195f3a0000070018111222233334444"
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    summary_file = exe_dir / "forensic_summary.md"
    summary_file.write_text(
        "**Workflow ID:** `wor_analysis`\n**Output Profile:** `prof_executive`\nSitra suomi analyysi",
        encoding="utf-8",
    )

    wf_id, locale = _extract_trace_metadata(trace_file)
    assert wf_id == "wor_analysis"
    assert locale == "fi"

    profile_id = _extract_profile_id(trace_file)
    assert profile_id == "prof_executive"


def test_extract_metadata_and_profile_from_reports_sdui(tmp_path: Path) -> None:
    """Test extracting workflow_id and profile_id from report.sdui.json."""
    from scripts.reconcile_storage import _extract_profile_id, _extract_trace_metadata

    exe_name = "exe_0195f3a0000070058555666677778888"
    exe_dir = tmp_path / "executions" / exe_name
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("[]", encoding="utf-8")

    reports_dir = tmp_path / "artifacts" / "reports" / "rep_01"
    reports_dir.mkdir(parents=True, exist_ok=True)
    sdui_file = reports_dir / "report.sdui.json"
    sdui_file.write_text(
        f'{{"execution_id": "{exe_name}", "workflow_id": "wor_custom_sdui", "profile_id": "prof_custom_sdui"}}',
        encoding="utf-8",
    )

    wf_id, _ = _extract_trace_metadata(trace_file)
    assert wf_id == "wor_custom_sdui"

    profile_id = _extract_profile_id(trace_file)
    assert profile_id == "prof_custom_sdui"


def test_load_execution_records_fallback_list_and_empty(tmp_path: Path) -> None:
    """Test loading records from legacy JSON list format and empty file."""
    from scripts.reconcile_storage import _load_execution_records

    empty_file = tmp_path / "empty.json"
    empty_file.write_text("", encoding="utf-8")
    assert _load_execution_records(empty_file) == []

    list_file = tmp_path / "list.json"
    record_json = {
        "id": "exe_0195f3a0000070018111222233334444",
        "workflow_id": "wor_default",
        "target_locale": "en",
        "output_profile_id": "prof_default",
        "execution_trace_storage_path": "executions/exe_0195f3a0000070018111222233334444/execution_trace.json",
    }
    list_file.write_text(json.dumps([record_json]), encoding="utf-8")
    records = _load_execution_records(list_file)
    assert len(records) == 1
    assert records[0].id == "exe_0195f3a0000070018111222233334444"


def test_reconstitute_execution_record_with_template(tmp_path: Path) -> None:
    """Test reconstituting execution record with template when workflow_id and profile_id exist."""
    from backend_v2.models.enums import ExecutionStatus
    from scripts.reconcile_storage import _reconstitute_execution_record

    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)
    exe_id = "exe_0195f3a00000700a8abbccddeeff0011"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    (exe_dir / "execution_trace.json").write_text("[]", encoding="utf-8")
    (exe_dir / "report.pdf").write_bytes(b"%PDF-1.4")
    (exe_dir / "context_variables.json").write_text("{}", encoding="utf-8")
    (exe_dir / "forensic_summary.md").write_text(
        "**Workflow ID:** `wor_custom_template`\n**Output Profile:** `prof_template`",
        encoding="utf-8",
    )

    template = ExecutionRecord(
        id="exe_0195f3a0000070008000000000000000",
        workflow_id="wor_original",
        target_locale="en",
        output_profile_id="prof_original",
        status=ExecutionStatus.PASSED,
    )
    rec = _reconstitute_execution_record(exe_id, storage_dir, template_record=template)
    assert rec.id == exe_id
    assert rec.workflow_id == "wor_custom_template"
    assert rec.output_profile_id == "prof_template"
    assert rec.pdf_report_path is not None
    assert rec.context_variables_storage_path is not None


def test_load_execution_records_invalid_json_error(tmp_path: Path) -> None:
    """Test that _load_execution_records returns empty list on malformed JSON and ReconciliationReport forbids extra fields."""
    from pydantic import ValidationError

    from scripts.reconcile_storage import _load_execution_records

    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("{invalid-json", encoding="utf-8")
    assert _load_execution_records(corrupt_file) == []

    with pytest.raises(ValidationError):
        ReconciliationReport.model_validate(
            {
                "db_path": "a",
                "storage_dir": "b",
                "is_synced": True,
                "unexpected_extra": "forbidden",
            }
        )


def test_reconcile_storage_main_cli_invalid_argument_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that CLI main() raises SystemExit(2) when conflicting --check and --fix flags are passed."""
    from scripts.reconcile_storage import main

    monkeypatch.setattr("sys.argv", ["reconcile_storage.py", "--check", "--fix"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2

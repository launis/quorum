"""Maintenance CLI tool for synchronizing database execution records and physical storage artifacts.

Adheres to V2 Architecture:
- 100% Pydantic V2 validated hydration (ExecutionRecord).
- Explicit UTF-8 TinyDB and file system encoding.
- Dual-mode operation: Safe read-only inspection (--check) vs. explicit recovery (--fix).
"""

import argparse
import io
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from tinydb import Query, TinyDB

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord

logger = logging.getLogger("scripts.reconcile_storage")


class TraceEventContent(BaseModel):
    """Header content of a trace event."""

    model_config = ConfigDict(strict=False, extra="ignore")

    language: str | None = None
    target_locale: str | None = None
    workflow_id: str | None = None


class TraceEventHeader(BaseModel):
    """Header structure of a trace event."""

    model_config = ConfigDict(strict=False, extra="ignore")

    step_name: str | None = None
    event_type: str | None = None
    content: TraceEventContent | None = None


class ReconciliationReport(BaseModel):
    """Encapsulates the audit and reconciliation outcome."""

    model_config = ConfigDict(strict=True, extra="forbid")

    db_path: str
    storage_dir: str
    orphaned_db_ids: list[str] = Field(default_factory=list)
    unindexed_disk_ids: list[str] = Field(default_factory=list)
    pruned_db_ids: list[str] = Field(default_factory=list)
    recovered_disk_ids: list[str] = Field(default_factory=list)
    is_synced: bool


def _extract_trace_metadata(trace_file: Path) -> tuple[str, str]:
    """Extracts target_locale and workflow_id from the initial trace event if present.

    Args:
        trace_file: Path to execution_trace.json.

    Returns:
        tuple of (workflow_id, target_locale).
    """
    workflow_id = "wor_default"
    target_locale = "en"
    try:
        raw_text = trace_file.read_text(encoding="utf-8")
        ta = TypeAdapter(list[TraceEventHeader])
        events = ta.validate_json(raw_text)
        if events and events[0].content:
            c = events[0].content
            target_locale = c.language or c.target_locale or "en"
            workflow_id = c.workflow_id or "wor_default"
    except OSError, json.JSONDecodeError, ValueError:
        pass
    return workflow_id, target_locale


def _resolve_trace_path(storage_dir: Path, exe_id: str, trace_path_raw: str | None) -> Path | None:
    """Resolves the physical trace file path on disk.

    Args:
        storage_dir: Base execution artifacts directory.
        exe_id: Canonical opaque execution ID.
        trace_path_raw: Raw storage path from the database record.

    Returns:
        Path if physical trace file exists on disk, None otherwise.
    """
    if trace_path_raw:
        direct_path = Path(trace_path_raw)
        if direct_path.exists():
            return direct_path
        parent_rel = storage_dir.parent / trace_path_raw
        if parent_rel.exists():
            return parent_rel

    default_disk_path = storage_dir / exe_id / "execution_trace.json"
    if default_disk_path.exists():
        return default_disk_path
    return None


def _reconstitute_execution_record(
    exe_id: str, storage_dir: Path, template_record: dict[str, Any] | None
) -> dict[str, Any]:
    """Constructs and validates an ExecutionRecord dictionary for an unindexed physical disk execution.

    Args:
        exe_id: Canonical opaque execution ID (e.g. 'exe_...').
        storage_dir: Base directory containing execution artifact folders.
        template_record: Optional existing database record used as structural template.

    Returns:
        Validated JSON-serializable dictionary representing the ExecutionRecord.
    """
    exe_dir = storage_dir / exe_id
    trace_file = exe_dir / "execution_trace.json"
    pdf_file = exe_dir / "report.pdf"
    cv_file = exe_dir / "context_variables.json"

    workflow_id, target_locale = _extract_trace_metadata(trace_file)

    trace_storage_path = f"executions/{exe_id}/execution_trace.json"
    cv_storage_path = f"executions/{exe_id}/context_variables.json" if cv_file.exists() else None
    pdf_storage_path = str(pdf_file).replace("\\", "/") if pdf_file.exists() else None
    status = ExecutionStatus.PASSED

    if template_record:
        rec_dict = dict(template_record)
        rec_dict["id"] = exe_id
        if workflow_id != "wor_default":
            rec_dict["workflow_id"] = workflow_id
        elif "workflow_id" not in rec_dict or not rec_dict["workflow_id"]:
            rec_dict["workflow_id"] = "wor_default"
        rec_dict["target_locale"] = target_locale
        rec_dict["status"] = status.value
        rec_dict["execution_trace_storage_path"] = trace_storage_path
        rec_dict["context_variables_storage_path"] = cv_storage_path
        rec_dict["pdf_report_path"] = pdf_storage_path
        rec_dict["steps"] = []
        rec_dict["execution_trace"] = []
        rec_dict["context_variables"] = {}
        rec_dict["frozen_context"] = None
        rec_dict["is_resumable"] = False
        now_iso = datetime.now(timezone.utc).isoformat()
        rec_dict["updated_at"] = now_iso
        if "created_at" not in rec_dict:
            rec_dict["created_at"] = now_iso
        if pdf_file.exists() and "completed_at" not in rec_dict:
            rec_dict["completed_at"] = now_iso
        record = ExecutionRecord.model_validate(rec_dict, strict=False)
    else:
        record = ExecutionRecord(
            id=exe_id,
            workflow_id=workflow_id,
            target_locale=target_locale,
            output_profile_id="prof_default",
            status=status,
            execution_trace_storage_path=trace_storage_path,
            context_variables_storage_path=cv_storage_path,
            pdf_report_path=pdf_storage_path,
            is_resumable=False,
            execution_trace=[],
            context_variables={},
            progress=None,
            status_message=None,
        )

    dumped: dict[str, Any] = record.model_dump(mode="json")
    return dumped


def reconcile_storage(
    db_path: Path, storage_dir: Path, fix: bool = False, logger_instance: logging.Logger | None = None
) -> ReconciliationReport:
    """Scans and synchronizes execution records in TinyDB with artifact folders on disk.

    Args:
        db_path: Path to TinyDB database file.
        storage_dir: Path to directory containing physical execution subdirectories.
        fix: If True, prunes orphaned database records and registers unindexed disk runs.
        logger_instance: Optional logger for emitting progress information.

    Returns:
        ReconciliationReport summarizing identified and remediated desynchronizations.
    """
    log = logger_instance or logger

    if not db_path.exists():
        log.warning("Database file '%s' does not exist.", db_path)
        return ReconciliationReport(
            db_path=str(db_path),
            storage_dir=str(storage_dir),
            is_synced=False,
        )

    db = TinyDB(str(db_path), encoding="utf-8")
    table = db.table("executions")
    records = table.all()

    db_execution_ids: set[str] = set()
    orphaned_db_ids: list[str] = []

    for rec in records:
        rec_id = rec["id"] if "id" in rec else None
        if not rec_id:
            continue
        db_execution_ids.add(str(rec_id))

        trace_path_raw = rec["execution_trace_storage_path"] if "execution_trace_storage_path" in rec else None
        resolved_trace = _resolve_trace_path(storage_dir, str(rec_id), trace_path_raw)
        if resolved_trace is None:
            orphaned_db_ids.append(str(rec_id))

    unindexed_disk_ids: list[str] = []
    if storage_dir.exists() and storage_dir.is_dir():
        for child in sorted(storage_dir.iterdir()):
            if child.is_dir() and (child / "execution_trace.json").exists():
                disk_id = child.name
                if disk_id not in db_execution_ids:
                    unindexed_disk_ids.append(disk_id)

    pruned_db_ids: list[str] = []
    recovered_disk_ids: list[str] = []

    if fix:
        execution_query = Query()
        for orphaned_id in orphaned_db_ids:
            table.remove(execution_query.id == orphaned_id)
            pruned_db_ids.append(orphaned_id)
            log.info("[Reconcile] Pruned orphaned DB record: %s", orphaned_id)

        template_record = records[0] if records else None
        for unindexed_id in unindexed_disk_ids:
            new_record_dict = _reconstitute_execution_record(unindexed_id, storage_dir, template_record)
            table.insert(new_record_dict)
            recovered_disk_ids.append(unindexed_id)
            log.info("[Reconcile] Recovered and registered disk execution: %s", unindexed_id)

    db.close()

    is_synced = (len(orphaned_db_ids) == 0 and len(unindexed_disk_ids) == 0) or (
        fix and len(pruned_db_ids) == len(orphaned_db_ids) and len(recovered_disk_ids) == len(unindexed_disk_ids)
    )

    return ReconciliationReport(
        db_path=str(db_path),
        storage_dir=str(storage_dir),
        orphaned_db_ids=orphaned_db_ids,
        unindexed_disk_ids=unindexed_disk_ids,
        pruned_db_ids=pruned_db_ids,
        recovered_disk_ids=recovered_disk_ids,
        is_synced=is_synced,
    )


def main() -> None:
    """Command-line interface entry point for execution storage reconciliation."""
    parser = argparse.ArgumentParser(
        description="Reconciles executions table in TinyDB with physical artifact folders in storage directory."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        default=True,
        help="Inspect synchronization state without modifying the database (default mode).",
    )
    group.add_argument(
        "--fix",
        action="store_true",
        help="Reconcile database: recover unindexed disk executions and prune orphaned records.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/db_v2.json"),
        help="Path to the TinyDB database file (defaults to data/db_v2.json).",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("data/files/executions"),
        help="Path to execution artifacts directory (defaults to data/files/executions).",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    is_fix = bool(args.fix)
    report = reconcile_storage(db_path=args.db_path, storage_dir=args.storage_dir, fix=is_fix)

    print("\n=== Storage & Database Reconciliation Audit ===")
    print(f"Database: {report.db_path}")
    print(f"Storage:  {report.storage_dir}")
    print(f"Mode:     {'FIX (Reconciliation)' if is_fix else 'CHECK (Dry-run inspection)'}")
    print(f"Status:   {'SYNCHRONIZED' if report.is_synced else 'DESYNCHRONIZED'}")
    print(f"Orphaned DB records:   {len(report.orphaned_db_ids)} {report.orphaned_db_ids}")
    print(f"Unindexed Disk runs:   {len(report.unindexed_disk_ids)} {report.unindexed_disk_ids}")

    if is_fix:
        print(f"Pruned DB records:     {len(report.pruned_db_ids)} {report.pruned_db_ids}")
        print(f"Recovered Disk runs:   {len(report.recovered_disk_ids)} {report.recovered_disk_ids}")
        print("\nReconciliation completed successfully.")
        sys.exit(0)
    else:
        if report.is_synced:
            print("\nDatabase and disk storage are 100% synchronized.")
            sys.exit(0)
        else:
            print("\nDesynchronization detected. Run with '--fix' to reconcile:")
            print(f"  uv run python scripts/reconcile_storage.py --fix --db-path {report.db_path}")
            sys.exit(1)


if __name__ == "__main__":
    main()

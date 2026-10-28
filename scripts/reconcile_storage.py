"""Maintenance CLI tool for synchronizing database execution records and physical storage artifacts.

Adheres to V2 Architecture:
- 100% Pydantic V2 validated hydration (ExecutionRecord).
- Explicit UTF-8 file system encoding.
- Dual-mode operation: Safe read-only inspection (--check) vs. explicit recovery (--fix).
"""

import argparse
import io
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

logger = logging.getLogger("scripts.reconcile_storage")

__all__ = [
    "ExecutionSnapshotDTO",
    "ReconciliationReport",
    "TraceEventContent",
    "TraceEventHeader",
    "main",
    "reconcile_storage",
]

# Resolve forward references in ExecutionRecord for strict ExecutionSnapshotDTO validation
ExecutionRecord.model_rebuild(
    _types_namespace={
        "ErrorTraceEvent": ErrorTraceEvent,
        "TombstoneEvent": TombstoneEvent,
        "TraceEvent": TraceEvent,
    }
)


class ExecutionSnapshotDTO(BaseModel):
    """Snapshot container for execution records.

    Attributes:
        executions: Indexed mapping of execution records.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    executions: dict[str, ExecutionRecord] = Field(
        default_factory=dict, description="Indexed mapping of execution records."
    )


ExecutionSnapshotDTO.model_rebuild()


class TraceEventContent(BaseModel):
    """Header content of a trace event.

    Attributes:
        language: Language identifier if present.
        target_locale: Target locale string if present.
        workflow_id: Workflow identifier if present.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    language: str | None = None
    target_locale: str | None = None
    workflow_id: str | None = None


class TraceEventHeader(BaseModel):
    """Header structure of a trace event.

    Attributes:
        step_name: Name of the executed workflow step.
        event_type: Category identifier of the event.
        content: Extracted header content if available.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_name: str | None = None
    event_type: str | None = None
    content: TraceEventContent | None = None


class ReconciliationReport(BaseModel):
    """Encapsulates the audit and reconciliation outcome.

    Attributes:
        db_path: Path to the execution snapshot file.
        storage_dir: Path to the physical storage directory.
        orphaned_db_ids: Execution IDs present in snapshot but missing from disk.
        unindexed_disk_ids: Execution IDs present on disk but missing from snapshot.
        pruned_db_ids: Execution IDs removed during fix mode.
        recovered_disk_ids: Execution IDs registered during fix mode.
        is_synced: True if storage artifacts and snapshot are fully synchronized.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    db_path: Annotated[str, Field(description="Path to the execution snapshot file.")]
    storage_dir: Annotated[str, Field(description="Path to the physical storage directory.")]
    orphaned_db_ids: list[str] = Field(
        default_factory=list, description="Execution IDs present in snapshot but missing from disk."
    )
    unindexed_disk_ids: list[str] = Field(
        default_factory=list, description="Execution IDs present on disk but missing from snapshot."
    )
    pruned_db_ids: list[str] = Field(default_factory=list, description="Execution IDs removed during fix mode.")
    recovered_disk_ids: list[str] = Field(default_factory=list, description="Execution IDs registered during fix mode.")
    is_synced: Annotated[bool, Field(description="True if storage artifacts and snapshot are fully synchronized.")]


def _extract_trace_metadata(trace_file: Path) -> tuple[str, str]:
    """Extracts target_locale and workflow_id from trace events or artifacts.

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
        for ev in events:
            if ev.content:
                c = ev.content
                if (c.language or c.target_locale) and target_locale == "en":
                    target_locale = c.language or c.target_locale or "en"
                if c.workflow_id and workflow_id == "wor_default":
                    workflow_id = c.workflow_id
    except OSError, json.JSONDecodeError, ValueError:
        pass

    if workflow_id == "wor_default":
        summary_file = trace_file.parent / "forensic_summary.md"
        if summary_file.exists():
            summary_text = summary_file.read_text(encoding="utf-8")
            match_wf = re.search(r"\*\*Workflow ID:\*\*\s*`?([a-zA-Z0-9_]+)`?", summary_text)
            if match_wf and workflow_id == "wor_default":
                workflow_id = match_wf.group(1)

    if workflow_id == "wor_default":
        reports_dir = trace_file.parent.parent.parent / "artifacts" / "reports"
        if reports_dir.exists():
            for rep_dir in reports_dir.iterdir():
                sdui_path = rep_dir / "report.sdui.json"
                if sdui_path.exists():
                    try:
                        sdui_text = sdui_path.read_text(encoding="utf-8")
                        if f'"{trace_file.parent.name}"' in sdui_text:
                            match_wf_sdui = re.search(r'"workflow_id":\s*"([^"]+)"', sdui_text)
                            if match_wf_sdui:
                                workflow_id = match_wf_sdui.group(1)
                                break
                    except OSError:
                        pass

    if target_locale == "en":
        summary_file = trace_file.parent / "forensic_summary.md"
        if summary_file.exists():
            stext = summary_file.read_text(encoding="utf-8").lower()
            if any(term in stext for term in ("megatrend", "sitra", "analyysi", "lopputuote", "suomi")):
                target_locale = "fi"

    return workflow_id, target_locale


def _extract_profile_id(trace_file: Path) -> str | None:
    """Extracts output profile ID from forensic summary or report SDUI if available.

    Args:
        trace_file: Path to execution_trace.json.

    Returns:
        Profile ID string if found, otherwise None.
    """
    summary_file = trace_file.parent / "forensic_summary.md"
    if summary_file.exists():
        summary_text = summary_file.read_text(encoding="utf-8")
        match_prf = re.search(r"\*\*Output Profile:\*\*\s*`?([a-zA-Z0-9_]+)`?", summary_text)
        if match_prf:
            return match_prf.group(1)

    reports_dir = trace_file.parent.parent.parent / "artifacts" / "reports"
    if reports_dir.exists():
        for rep_dir in reports_dir.iterdir():
            sdui_path = rep_dir / "report.sdui.json"
            if sdui_path.exists():
                try:
                    sdui_text = sdui_path.read_text(encoding="utf-8")
                    if f'"{trace_file.parent.name}"' in sdui_text:
                        match_prf_sdui = re.search(r'"profile_id":\s*"([^"]+)"', sdui_text)
                        if match_prf_sdui:
                            return match_prf_sdui.group(1)
                except OSError:
                    pass
    return None


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
    exe_id: str, storage_dir: Path, template_record: ExecutionRecord | None
) -> ExecutionRecord:
    """Constructs and validates an ExecutionRecord for an unindexed physical disk execution.

    Args:
        exe_id: Canonical opaque execution ID (e.g. 'exe_...').
        storage_dir: Base directory containing execution artifact folders.
        template_record: Optional existing ExecutionRecord used as structural template.

    Returns:
        Validated ExecutionRecord instance.
    """
    exe_dir = storage_dir / exe_id
    trace_file = exe_dir / "execution_trace.json"
    pdf_file = exe_dir / "report.pdf"
    cv_file = exe_dir / "context_variables.json"

    workflow_id, target_locale = _extract_trace_metadata(trace_file)
    profile_id = _extract_profile_id(trace_file)

    trace_storage_path = f"executions/{exe_id}/execution_trace.json"
    cv_storage_path = f"executions/{exe_id}/context_variables.json" if cv_file.exists() else None
    pdf_storage_path = str(pdf_file).replace("\\", "/") if pdf_file.exists() else None
    status = ExecutionStatus.PASSED

    if template_record is not None:
        now_dt = datetime.now(timezone.utc)
        resolved_wf_id = (
            workflow_id
            if workflow_id != "wor_default"
            else (template_record.workflow_id if template_record.workflow_id else "wor_default")
        )
        resolved_prf_id = profile_id if profile_id else template_record.output_profile_id
        completed_dt = (
            template_record.completed_at
            if template_record.completed_at is not None
            else (now_dt if pdf_file.exists() else None)
        )
        return template_record.model_copy(
            update={
                "id": exe_id,
                "workflow_id": resolved_wf_id,
                "output_profile_id": resolved_prf_id,
                "target_locale": target_locale,
                "status": status,
                "execution_trace_storage_path": trace_storage_path,
                "context_variables_storage_path": cv_storage_path,
                "pdf_report_path": pdf_storage_path,
                "steps": [],
                "execution_trace": [],
                "context_variables": ContextVariablesDTO(),
                "frozen_context": None,
                "is_resumable": False,
                "updated_at": now_dt,
                "completed_at": completed_dt,
            }
        )

    return ExecutionRecord(
        id=exe_id,
        workflow_id=workflow_id,
        target_locale=target_locale,
        output_profile_id=profile_id or "prof_default",
        status=status,
        execution_trace_storage_path=trace_storage_path,
        context_variables_storage_path=cv_storage_path,
        pdf_report_path=pdf_storage_path,
        is_resumable=False,
        execution_trace=[],
        context_variables=ContextVariablesDTO(),
        progress=None,
        status_message=None,
    )


def _load_execution_records(db_path: Path) -> list[ExecutionRecord]:
    """Loads ExecutionRecord models from a JSON snapshot file.

    Args:
        db_path: Path to JSON snapshot file.

    Returns:
        List of validated ExecutionRecord instances.
    """
    raw_text = db_path.read_text(encoding="utf-8").strip()
    if not raw_text:
        return []
    try:
        snapshot = ExecutionSnapshotDTO.model_validate_json(raw_text)
        return list(snapshot.executions.values())
    except ValidationError, ValueError:
        pass
    try:
        return TypeAdapter(list[ExecutionRecord]).validate_json(raw_text)
    except ValidationError, ValueError:
        pass
    return []


def _save_execution_records(db_path: Path, records: list[ExecutionRecord]) -> None:
    """Persists ExecutionRecord models to a JSON snapshot file.

    Args:
        db_path: Path to JSON snapshot file.
        records: List of ExecutionRecord instances.
    """
    indexed = {str(idx): rec.model_dump(mode="json") for idx, rec in enumerate(records, start=1)}
    db_path.write_text(json.dumps({"executions": indexed}, indent=2), encoding="utf-8")


def reconcile_storage(
    db_path: Path, storage_dir: Path, fix: bool = False, logger_instance: logging.Logger | None = None
) -> ReconciliationReport:
    """Scans and synchronizes execution records with artifact folders on disk.

    Args:
        db_path: Path to execution records snapshot file.
        storage_dir: Path to directory containing physical execution subdirectories.
        fix: If True, prunes orphaned records and registers unindexed disk runs.
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

    records = _load_execution_records(db_path)

    db_execution_ids: set[str] = set()
    orphaned_db_ids: list[str] = []

    for rec in records:
        rec_id = rec.id
        if not rec_id:
            continue
        db_execution_ids.add(rec_id)

        trace_path_raw = rec.execution_trace_storage_path
        resolved_trace = _resolve_trace_path(storage_dir, rec_id, trace_path_raw)
        if resolved_trace is None:
            orphaned_db_ids.append(rec_id)

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
        orphaned_set = set(orphaned_db_ids)
        remaining_records = [r for r in records if r.id not in orphaned_set]
        for orphaned_id in orphaned_db_ids:
            pruned_db_ids.append(orphaned_id)
            log.info("[Reconcile] Pruned orphaned DB record: %s", orphaned_id)

        template_record = records[0] if records else None
        for unindexed_id in unindexed_disk_ids:
            new_record = _reconstitute_execution_record(unindexed_id, storage_dir, template_record)
            remaining_records.append(new_record)
            recovered_disk_ids.append(unindexed_id)
            log.info("[Reconcile] Recovered and registered disk execution: %s", unindexed_id)

        _save_execution_records(db_path, remaining_records)

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


def main(argv: list[str] | None = None) -> None:
    """Command-line interface entry point for execution storage reconciliation.

    Args:
        argv: Optional command-line argument list (defaults to sys.argv[1:]).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Executions Snapshot and Physical Storage Reconciliation Suite.\n\n"
            "Maintains CQRS consistency between operational database records and physical file artifacts."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        default=Path("data/executions_snapshot.json"),
        help="Path to the execution snapshot file.",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("data/files/executions"),
        help="Path to execution artifacts directory (defaults to data/files/executions).",
    )

    args = parser.parse_args(argv)
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

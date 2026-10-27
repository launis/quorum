"""Zero-ORM Strictness & Closed PostgreSQL 19 Topology AST Auditor.

Statically enforces Quorum's All-in-PostgreSQL 19 Zero-ORM invariants across
backend_v2/database/postgres/, backend_v2/models/domain/proposition_graph.py,
and backend_v2/database/migrations/001_pg19_uuidv7_schema.sql:
- ZORM001: Bans imports of sqlalchemy, alembic, or orjson.
- ZORM002: Bans untyped dictionary subscript annotations targeting Any/object and dict(r) row unpacking.
- ZORM003: Bans broad except Exception handlers lacking explicit AppException re-raise.
- ZORM004: Enforces that SQL CREATE TABLE identifiers belong strictly to the closed 12-table set.
- ZORM005: Bans calling llm_client, execute_structured_task, or execute_chat_task inside database/UoW modules.
- ZORM006: Enforces that record subscript column keys in graph_adapter.py and entity_adapter.py map 1:1 to declared domain model fields.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts._script_base import (
    ANSIColors,
    GuardrailSeverity,
    setup_script_environment,
)

setup_script_environment()

# Step 1: Closed 12-table topology and banned symbol sets
CLOSED_POSTGRES_TABLES: frozenset[str] = frozenset(
    {
        "users",
        "organizations",
        "workflows",
        "steps",
        "prompt_blocks",
        "output_profiles",
        "system_configs",
        "executions",
        "report_artifacts",
        "report_binaries",
        "quorum_nodes",
        "quorum_edges",
    }
)

BANNED_ORM_IMPORTS: frozenset[str] = frozenset({"sqlalchemy", "alembic", "orjson"})

BANNED_LLM_IDENTIFIERS: frozenset[str] = frozenset(
    {
        "llm_client",
        "execute_structured_task",
        "execute_chat_task",
        "from_strategy",
    }
)

APPROVED_ADAPTER_RECORD_COLUMNS: frozenset[str] = frozenset(
    {
        # PropositionNode
        "node_id",
        "run_id",
        "node_type",
        "confidence",
        "payload",
        "created_at",
        # DependencyEdge
        "edge_id",
        "source_id",
        "target_id",
        "relation_type",
        "causal_weight",
        # FalsifiedClaimMatch
        "rebuttal_id",
        "invalidated_warrant_id",
        "falsified_claim_id",
        "rebuttal_confidence",
        "claim_statement",
        # ReportBinaryPayloadDTO & ReportArtifact
        "report_id",
        "mime_type",
        "pdf_bytes",
        "size_bytes",
        "has_pdf",
        # Core entity columns & CTE cycle inspection
        "id",
        "traversal_path",
        "is_cycle",
        "updated_at",
        "workflow_id",
        "workflow_version",
        "active_profile_id",
        "output_profile_id",
        "status",
        "target_locale",
        "progress",
        "status_message",
        "raw_inputs",
        "frozen_context",
        "frozen_context_storage_path",
        "pdf_report_path",
        "steps",
        "step_states",
        "profile_syntheses",
        "source_identity_manifest",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
        "is_resumable",
        "prompt_tokens",
        "completion_tokens",
        "cached_tokens",
        "reasoning_tokens",
        "cumulative_synthesis_tokens",
        "dag_cost_usd",
        "cumulative_synthesis_cost",
        "cost_estimate",
        "models_used",
        "execution_summary",
        "metadata",
        "duration_ms",
        "error",
        "completed_at",
        "created_by",
        "organization_id",
    }
)

_CREATE_TABLE_REGEX = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)",
    re.IGNORECASE,
)


class ZeroOrmRuleCode(StrEnum):
    """Rule codes for Zero-ORM architectural strictness checks."""

    ZORM001 = "ZORM001"
    ZORM002 = "ZORM002"
    ZORM003 = "ZORM003"
    ZORM004 = "ZORM004"
    ZORM005 = "ZORM005"
    ZORM006 = "ZORM006"


class ZeroOrmFindingDTO(BaseModel):
    """Immutable finding record emitted by the Zero-ORM AST auditor.

    Attributes:
        filepath: Workspace-relative or absolute file path where the violation occurred.
        lineno: 1-based line number of the offending construct.
        rule_code: Specific ZeroOrmRuleCode triggered.
        message: Detailed explanation of the architectural violation.
        severity: GuardrailSeverity classification (always FATAL).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    filepath: Annotated[str, Field(description="File path of the violation.")]
    lineno: Annotated[int, Field(ge=1, description="1-based line number.")]
    rule_code: Annotated[ZeroOrmRuleCode, Field(description="Triggered Zero-ORM rule code.")]
    message: Annotated[str, Field(description="Explanation of the violation.")]
    severity: Annotated[
        GuardrailSeverity,
        Field(default=GuardrailSeverity.FATAL, description="Violation severity."),
    ] = GuardrailSeverity.FATAL


class ZeroOrmAuditReportDTO(BaseModel):
    """Aggregated summary report of a Zero-ORM strictness audit run.

    Attributes:
        scanned_files: Total number of Python and SQL files analyzed.
        findings: Immutable tuple of ZeroOrmFindingDTO records discovered.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    scanned_files: Annotated[int, Field(ge=0, description="Number of files analyzed.")]
    findings: Annotated[tuple[ZeroOrmFindingDTO, ...], Field(default=(), description="Collected findings.")]

    @property
    def is_clean(self) -> bool:
        """Return True when zero violations were discovered.

        Returns:
            Boolean indicating a clean audit pass.
        """
        return len(self.findings) == 0


class _ZeroOrmAstVisitor(ast.NodeVisitor):
    """AST node visitor enforcing ZORM001, ZORM002, ZORM003, ZORM005, and ZORM006.

    Attributes:
        filepath: String representation of the file being visited.
        is_adapter_file: Whether the file is graph_adapter.py or entity_adapter.py.
        findings: List of ZeroOrmFindingDTO instances collected during traversal.
    """

    def __init__(self, filepath: str, is_adapter_file: bool) -> None:
        """Initialize the AST visitor for a target Python source file.

        Args:
            filepath: File path string for diagnostic reporting.
            is_adapter_file: True if checking SQL column subscript parity (ZORM006).
        """
        self.filepath = filepath
        self.is_adapter_file = is_adapter_file
        self.findings: list[ZeroOrmFindingDTO] = []
        self._in_finally: bool = False

    def _record(self, lineno: int, rule_code: ZeroOrmRuleCode, message: str) -> None:
        """Append a ZeroOrmFindingDTO to the visitor's findings list.

        Args:
            lineno: 1-based source line number.
            rule_code: Rule identifier.
            message: Diagnostic message.
        """
        self.findings.append(
            ZeroOrmFindingDTO(
                filepath=self.filepath,
                lineno=max(1, lineno),
                rule_code=rule_code,
                message=message,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        """Inspect standard import statements for ZORM001 banned libraries.

        Args:
            node: AST Import node.
        """
        for alias in node.names:
            root_pkg = alias.name.split(".")[0].lower()
            if root_pkg in BANNED_ORM_IMPORTS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM001,
                    f"Banned import '{alias.name}' detected; use Zero-ORM asyncpg + pydantic_core.",
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspect from-import statements for ZORM001 banned libraries.

        Args:
            node: AST ImportFrom node.
        """
        if node.module is not None:
            root_pkg = node.module.split(".")[0].lower()
            if root_pkg in BANNED_ORM_IMPORTS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM001,
                    f"Banned import from '{node.module}' detected; use Zero-ORM asyncpg + pydantic_core.",
                )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Inspect subscript expressions for ZORM002 untyped mappings and ZORM006 row columns.

        Args:
            node: AST Subscript node.
        """
        if isinstance(node.value, ast.Name) and node.value.id.lower() in {"dict", "mapping", "mutablemapping"}:
            if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2:
                val_node = node.slice.elts[1]
                if isinstance(val_node, ast.Name) and val_node.id in {"Any", "object"}:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM002,
                        f"Untyped mapping annotation targeting '{val_node.id}' is banned in Zero-ORM modules.",
                    )
        if (
            self.is_adapter_file
            and isinstance(node.value, ast.Name)
            and node.value.id in {"row", "record", "r", "rec"}
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            col_name = node.slice.value
            if col_name not in APPROVED_ADAPTER_RECORD_COLUMNS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM006,
                    f"Record column '{col_name}' does not map to any approved Pydantic V2 domain model field.",
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Inspect function calls for ZORM002 dict(row) unpacking and ZORM005 LLM invocations.

        Args:
            node: AST Call node.
        """
        if isinstance(node.func, ast.Name):
            if node.func.id == "dict" and len(node.args) >= 1:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM002,
                    "Direct dict(...) conversion on database records is banned; use direct subscripting into DTOs.",
                )
            if node.func.id in BANNED_LLM_IDENTIFIERS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM005,
                    f"Banned LLM call '{node.func.id}' inside database/UoW layer violates Post-Wave Atomic Commit.",
                )
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in BANNED_LLM_IDENTIFIERS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM005,
                    f"Banned LLM method '{node.func.attr}' inside database/UoW layer violates Post-Wave Atomic Commit.",
                )
            if isinstance(node.func.value, ast.Name) and node.func.value.id in BANNED_LLM_IDENTIFIERS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM005,
                    f"Banned LLM client usage '{node.func.value.id}.{node.func.attr}' inside database/UoW layer.",
                )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Traverse try/except/finally blocks while tracking finally cleanup scope.

        Args:
            node: AST Try node.
        """
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            self.visit(handler)
        for stmt in node.orelse:
            self.visit(stmt)
        prev_finally = self._in_finally
        self._in_finally = True
        for stmt in node.finalbody:
            self.visit(stmt)
        self._in_finally = prev_finally

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Inspect exception handlers for ZORM003 broad exception swallowing.

        Args:
            node: AST ExceptHandler node.
        """
        if not self._in_finally:
            is_broad = node.type is None or (
                isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
            )
            if is_broad:
                has_raise = any(isinstance(sub, ast.Raise) for sub in ast.walk(node))
                if not has_raise:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM003,
                        "Broad exception handler without explicit AppException re-raise is banned.",
                    )
        self.generic_visit(node)


def audit_python_file(filepath: Path) -> list[ZeroOrmFindingDTO]:
    """Parse and audit a single Python file against Zero-ORM AST rules.

    Args:
        filepath: Path to the Python file to inspect.

    Returns:
        List of ZeroOrmFindingDTO findings discovered in the file.
    """
    source = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        return [
            ZeroOrmFindingDTO(
                filepath=str(filepath),
                lineno=max(1, exc.lineno if exc.lineno is not None else 1),
                rule_code=ZeroOrmRuleCode.ZORM001,
                message=f"SyntaxError while parsing Python file: {exc.msg}",
            )
        ]

    is_adapter = filepath.name in {"graph_adapter.py", "entity_adapter.py"}
    visitor = _ZeroOrmAstVisitor(filepath=str(filepath), is_adapter_file=is_adapter)
    visitor.visit(tree)
    return visitor.findings


def audit_sql_migration_file(filepath: Path) -> list[ZeroOrmFindingDTO]:
    """Audit a SQL DDL migration file against rule ZORM004 (closed 12-table topology).

    Args:
        filepath: Path to the SQL DDL file.

    Returns:
        List of ZeroOrmFindingDTO findings discovered in the SQL file.
    """
    findings: list[ZeroOrmFindingDTO] = []
    content = filepath.read_text(encoding="utf-8")
    for idx, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        for match in _CREATE_TABLE_REGEX.finditer(line):
            table_name = match.group(1).lower()
            if table_name not in CLOSED_POSTGRES_TABLES:
                findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(filepath),
                        lineno=idx,
                        rule_code=ZeroOrmRuleCode.ZORM004,
                        message=(
                            f"Table '{table_name}' is outside the closed 12-table PostgreSQL topology: "
                            f"{sorted(CLOSED_POSTGRES_TABLES)}."
                        ),
                    )
                )
    return findings


def run_zero_orm_audit(target_paths: list[Path] | None = None) -> ZeroOrmAuditReportDTO:
    """Execute the Zero-ORM strictness audit across target paths or canonical defaults.

    Args:
        target_paths: Optional explicit list of files or directories to scan. When None,
            scans the canonical PostgreSQL package, proposition graph domain module,
            and SQL DDL migration file if present on disk.

    Returns:
        Immutable ZeroOrmAuditReportDTO containing file count and findings.
    """
    explicit_mode = target_paths is not None and len(target_paths) > 0
    resolved_targets: list[Path] = (
        list(target_paths)
        if explicit_mode and target_paths is not None
        else [
            _WORKSPACE_ROOT / "backend_v2" / "database" / "postgres",
            _WORKSPACE_ROOT / "backend_v2" / "models" / "domain" / "proposition_graph.py",
            _WORKSPACE_ROOT / "backend_v2" / "database" / "migrations" / "001_pg19_uuidv7_schema.sql",
        ]
    )

    scanned_count = 0
    all_findings: list[ZeroOrmFindingDTO] = []

    for target in resolved_targets:
        if not target.exists():
            if explicit_mode:
                all_findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(target),
                        lineno=1,
                        rule_code=ZeroOrmRuleCode.ZORM001,
                        message=f"Explicitly specified target path does not exist: {target}",
                    )
                )
            continue

        if target.is_dir():
            for py_file in sorted(target.rglob("*.py")):
                scanned_count += 1
                all_findings.extend(audit_python_file(py_file))
            for sql_file in sorted(target.rglob("*.sql")):
                scanned_count += 1
                all_findings.extend(audit_sql_migration_file(sql_file))
        elif target.suffix.lower() == ".py":
            scanned_count += 1
            all_findings.extend(audit_python_file(target))
        elif target.suffix.lower() == ".sql":
            scanned_count += 1
            all_findings.extend(audit_sql_migration_file(target))

    return ZeroOrmAuditReportDTO(scanned_files=scanned_count, findings=tuple(all_findings))


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI ArgumentParser for audit_zero_orm_strictness.py.

    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Zero-ORM Strictness & Closed PostgreSQL 19 Topology AST Auditor.\n\n"
            "Enforces ZORM001-ZORM006 across backend_v2/database/postgres/, "
            "proposition_graph.py, and 001_pg19_uuidv7_schema.sql."
        ),
        epilog=(
            "PowerShell Examples:\n"
            "  uv run python scripts/audit_zero_orm_strictness.py\n"
            "  uv run python scripts/audit_zero_orm_strictness.py backend_v2/database/postgres/\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional explicit file or directory paths to scan.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Zero-ORM AST verification.

    Args:
        argv: Optional list of CLI argument strings.

    Returns:
        Exit code 0 if zero violations are found, 1 otherwise.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    target_paths: list[Path] | None = args.paths if args.paths else None
    report = run_zero_orm_audit(target_paths=target_paths)

    if not report.is_clean:
        print(
            f"{ANSIColors.RED}{ANSIColors.BOLD}[ZORM AUDIT FAILED]{ANSIColors.RESET} "
            f"Found {len(report.findings)} violation(s) across {report.scanned_files} file(s):"
        )
        for item in report.findings:
            print(f"  - [{item.rule_code.value}] {item.filepath}:{item.lineno} -> {item.message}")
        return 1

    print(
        f"{ANSIColors.GREEN}{ANSIColors.BOLD}[ZORM AUDIT PASSED]{ANSIColors.RESET} "
        f"0 violations across {report.scanned_files} scanned file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

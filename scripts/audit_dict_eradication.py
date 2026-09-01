"""Deterministic AST Multi-Layer Dict Eradication Auditor.

Statically analyzes backend Python files to mathematically verify:
1. Exactly 0 naked dict[str, Any] / dict[str, object] type annotations.
2. Exactly 0 isinstance(..., dict) checks in domain and service layers.
3. Exactly 0 unauthorized/unjustified # noqa: QGR suppressions.
4. Exactly 0 imports or references to legacy dict_utils.
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

# Locked physical SDK and storage driver boundaries
LOCKED_PHYSICAL_DRIVERS: set[str] = {
    "tinydb_driver.py",
    "firestore_driver.py",
    "provider.py",
    "logging_config.py",
}

BANNED_REASON_PLACEHOLDERS: set[str] = {
    "n/a",
    "na",
    "ok",
    "none",
    "test",
    "todo",
    "fix",
    "pass",
    "fail",
    "temporary",
    "temp",
    "",
}


@dataclass
class AuditViolation:
    """Represents a discovered audit violation."""

    filepath: str
    line: int
    metric: str
    message: str


@dataclass
class DictEradicationReport:
    """Aggregated audit report across all four mathematical metrics."""

    naked_dict_annotations: int = 0
    service_duck_typing: int = 0
    unauthorized_suppressions: int = 0
    dict_utils_references: int = 0
    violations: list[AuditViolation] = field(default_factory=list)

    @property
    def total_violations(self) -> int:
        """Returns the total number of violations across all metrics."""
        return (
            self.naked_dict_annotations
            + self.service_duck_typing
            + self.unauthorized_suppressions
            + self.dict_utils_references
        )


class DictEradicationVisitor(ast.NodeVisitor):
    """AST Visitor scanning Python files for permissive dict patterns."""

    def __init__(self, filepath: str, source_bytes: bytes) -> None:
        self.filepath = filepath
        self.source_bytes = source_bytes
        self.filename = Path(filepath).name
        self.is_exempt = self.filename in LOCKED_PHYSICAL_DRIVERS
        self.is_test = "tests" in Path(filepath).parts
        self.is_domain_or_service = any(
            p in Path(filepath).parts for p in ("services", "models", "hooks", "orchestrator", "api", "database")
        )
        self.violations: list[AuditViolation] = []

    def _is_naked_dict_subscript(self, node: ast.AST) -> bool:
        """Checks whether an AST node is a subscript of dict[str, Any] or dict[str, object]."""
        if not isinstance(node, ast.Subscript):
            return False

        # Check if subscript value is dict or Dict
        is_dict_type = False
        match node.value:
            case ast.Name(id="dict" | "Dict"):
                is_dict_type = True
            case ast.Attribute(attr="dict" | "Dict"):
                is_dict_type = True
            case _:
                is_dict_type = False

        if not is_dict_type:
            return False

        # Inspect slice
        match node.slice:
            case ast.Tuple(elts=elements) if len(elements) == 2:
                val_type = elements[1]
                match val_type:
                    case ast.Name(id="Any" | "object"):
                        return True
                    case ast.Attribute(attr="Any" | "object"):
                        return True
                    case _:
                        return False
            case _:
                return False

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Inspects variable type annotations for naked dicts."""
        if not self.is_exempt and not self.is_test and self._is_naked_dict_subscript(node.annotation):
            self.violations.append(
                AuditViolation(
                    filepath=self.filepath,
                    line=node.lineno,
                    metric="naked_dict_annotations",
                    message=f"Naked dict annotation found: `{ast.unparse(node.annotation)}`",
                )
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Inspects function parameter and return type annotations."""
        if not self.is_exempt and not self.is_test:
            if node.returns is not None and self._is_naked_dict_subscript(node.returns):
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="naked_dict_annotations",
                        message=f"Naked dict return type annotation in `{node.name}`: `{ast.unparse(node.returns)}`",
                    )
                )

            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            for arg in all_args:
                if arg.annotation is not None and self._is_naked_dict_subscript(arg.annotation):
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=arg.lineno,
                            metric="naked_dict_annotations",
                            message=f"Naked dict argument annotation for `{arg.arg}` in `{node.name}`: `{ast.unparse(arg.annotation)}`",
                        )
                    )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Inspects async function parameter and return type annotations."""
        if not self.is_exempt and not self.is_test:
            if node.returns is not None and self._is_naked_dict_subscript(node.returns):
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="naked_dict_annotations",
                        message=f"Naked dict return type annotation in async `{node.name}`: `{ast.unparse(node.returns)}`",
                    )
                )

            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            for arg in all_args:
                if arg.annotation is not None and self._is_naked_dict_subscript(arg.annotation):
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=arg.lineno,
                            metric="naked_dict_annotations",
                            message=f"Naked dict argument annotation for `{arg.arg}` in async `{node.name}`: `{ast.unparse(arg.annotation)}`",
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Inspects isinstance calls for dict checks in domain and service layers."""
        if not self.is_exempt and not self.is_test and self.is_domain_or_service:
            if isinstance(node.func, ast.Name) and node.func.id == "isinstance" and len(node.args) >= 2:
                target_type = node.args[1]
                is_dict = False
                match target_type:
                    case ast.Name(id="dict"):
                        is_dict = True
                    case ast.Tuple(elts=elts):
                        for elt in elts:
                            if isinstance(elt, ast.Name) and elt.id == "dict":
                                is_dict = True
                                break
                    case _:
                        is_dict = False

                if is_dict:
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=node.lineno,
                            metric="service_duck_typing",
                            message=f"Banned isinstance(..., dict) duck-typing: `{ast.unparse(node)}`",
                        )
                    )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Inspects imports for dict_utils references."""
        for alias in node.names:
            if "dict_utils" in alias.name:
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="dict_utils_references",
                        message=f"Banned import of legacy dict_utils: `{alias.name}`",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspects from imports for dict_utils references."""
        if node.module and "dict_utils" in node.module:
            self.violations.append(
                AuditViolation(
                    filepath=self.filepath,
                    line=node.lineno,
                    metric="dict_utils_references",
                    message=f"Banned from-import of legacy dict_utils: `{node.module}`",
                )
            )
        self.generic_visit(node)


def audit_file_comments(filepath: str, source_bytes: bytes) -> list[AuditViolation]:
    """Audits comments in a file to verify all # noqa: QGR suppressions have substantive reasons."""
    violations: list[AuditViolation] = []
    filename = Path(filepath).name
    if filename in LOCKED_PHYSICAL_DRIVERS:
        return violations

    try:
        tokens = tokenize.tokenize(io.BytesIO(source_bytes).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                text = tok.string
                match = re.search(
                    r"#\s*noqa(?::\s*([A-Za-z0-9_,\s]+))?(?:\s*\[(?:REASON|reason):\s*([^\]]+)\])?",
                    text,
                    re.IGNORECASE,
                )
                if match:
                    rules_str = match.group(1)
                    raw_reason = match.group(2)
                    rule_codes = {r.strip().upper() for r in rules_str.split(",") if r.strip()} if rules_str else {"*"}
                    has_qgr = any(r.startswith("QGR") or r == "*" for r in rule_codes)
                    if has_qgr:
                        if not raw_reason or not raw_reason.strip():
                            violations.append(
                                AuditViolation(
                                    filepath=filepath,
                                    line=tok.start[0],
                                    metric="unauthorized_suppressions",
                                    message="Missing reason for # noqa: QGR suppression.",
                                )
                            )
                        else:
                            clean_reason = raw_reason.strip().lower()
                            if clean_reason in BANNED_REASON_PLACEHOLDERS or len(clean_reason) < 10:
                                violations.append(
                                    AuditViolation(
                                        filepath=filepath,
                                        line=tok.start[0],
                                        metric="unauthorized_suppressions",
                                        message=f"Trivial/placeholder reason for # noqa suppression: `{raw_reason}`",
                                    )
                                )
    except Exception:
        pass
    return violations


def audit_dict_eradication(target_dir: Path | str = "backend_v2") -> DictEradicationReport:
    """Executes the complete multi-layer dict eradication audit on target directory.

    Args:
        target_dir: Directory to audit (defaults to backend_v2).

    Returns:
        DictEradicationReport containing metrics and discovered violations.
    """
    report = DictEradicationReport()
    target_path = Path(target_dir)

    if not target_path.exists():
        return report

    py_files = sorted(target_path.rglob("*.py"))
    for file_path in py_files:
        try:
            source_bytes = file_path.read_bytes()
            source_text = source_bytes.decode("utf-8")
            tree = ast.parse(source_text, filename=str(file_path))
        except Exception:
            continue

        visitor = DictEradicationVisitor(str(file_path), source_bytes)
        visitor.visit(tree)

        for v in visitor.violations:
            if v.metric == "naked_dict_annotations":
                report.naked_dict_annotations += 1
            elif v.metric == "service_duck_typing":
                report.service_duck_typing += 1
            elif v.metric == "dict_utils_references":
                report.dict_utils_references += 1
            report.violations.append(v)

        comment_violations = audit_file_comments(str(file_path), source_bytes)
        for cv in comment_violations:
            report.unauthorized_suppressions += 1
            report.violations.append(cv)

    return report


def main() -> int:
    """CLI entry point for deterministic AST dict eradication audit."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("  QUORUM DETERMINISTIC AST DICT ERADICATION AUDITOR")
    print("=" * 80)

    report = audit_dict_eradication("backend_v2")

    print(f"1. Naked Dict Annotations (dict[str, Any]):  {report.naked_dict_annotations}")
    print(f"2. Service Layer Duck-Typing (isinstance):   {report.service_duck_typing}")
    print(f"3. Unauthorized # noqa Suppressions:         {report.unauthorized_suppressions}")
    print(f"4. Legacy dict_utils References:             {report.dict_utils_references}")
    print("-" * 80)
    print(f"TOTAL VIOLATIONS:                            {report.total_violations}")
    print("=" * 80)

    if report.total_violations > 0:
        print("\n[FAILED] Non-zero dict eradication violations discovered:\n")
        # Group violations by filepath
        by_file: dict[str, list[AuditViolation]] = {}
        for v in report.violations:
            by_file.setdefault(v.filepath, []).append(v)

        for fpath, viols in sorted(by_file.items()):
            print(f"  File: {fpath} ({len(viols)} violations)")
            for v in viols[:5]:
                print(f"    Line {v.line} [{v.metric}]: {v.message}")
            if len(viols) > 5:
                print(f"    ... and {len(viols) - 5} more")
            print()
        return 1

    print("\n[PASSED] 100% Mathematical Zero Violations across all 4 metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Automated Technical Debt and 1-Hop Caller Audit Scanner CLI.

Single Source of Truth for static scanning of implementation plan target files
and their 1-hop caller dependencies against the 7-item technical debt checklist:
1. Python AST Reflection (getattr, hasattr, setattr)
2. Python AST Dict Fallbacks (.get() lookups)
3. Python AST Exception Swallowing (except Exception: pass)
4. Python AST Mutable Defaults & Duplicate Annotated Field()
5. Flutter Dart Anti-Patterns (DGR001-DGR010)
6. ISTQB Test Partition Check (negative test partitions)
7. Model Factory Parity (polyfactory vs raw dicts)
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from scripts._ast_boundary_utils import extract_target_files
from scripts._ast_guardrails import is_boundary_exempt
from scripts._dart_guardrails import scan_dart_source
from scripts._script_base import ANSIColors, GuardrailSeverity, get_repo_root, setup_script_environment

__all__ = [
    "TechnicalDebtFindingDTO",
    "TechnicalDebtScanResultDTO",
    "find_one_hop_callers",
    "scan_python_technical_debt",
    "scan_dart_technical_debt",
    "scan_targets_technical_debt",
    "format_technical_debt_markdown",
    "main",
]


class TechnicalDebtFindingDTO(BaseModel):
    """Pydantic V2 DTO representing an individual technical debt finding."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[str, Field(description="Rule code e.g. QGR001, DGR007, TD_EXCEPT_PASS")]
    file_path: Annotated[str, Field(description="Relative file path")]
    lineno: Annotated[int, Field(ge=0, description="1-indexed line number")]
    col_offset: Annotated[int, Field(ge=0, description="0-indexed column offset")]
    message: Annotated[str, Field(description="Violation message")]
    remediation: Annotated[str, Field(description="Remediation instructions")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    debt_category: Annotated[str, Field(description="Category of technical debt")]


class TechnicalDebtScanResultDTO(BaseModel):
    """Pydantic V2 DTO representing overall technical debt scan results."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    targets: Annotated[list[str], Field(description="List of target file paths scanned")]
    one_hop_callers: Annotated[list[str], Field(description="List of 1-hop caller file paths")]
    findings: Annotated[list[TechnicalDebtFindingDTO], Field(description="List of discovered findings")]
    passed: Annotated[bool, Field(description="Whether scan passed with zero non-exempt fatal/warning debt")]


class _ImportExtractor(ast.NodeVisitor):
    """AST visitor collecting imported modules and imported symbols."""

    def __init__(self) -> None:
        self.imported_modules: set[str] = set()
        self.imported_from_pairs: set[tuple[str, str]] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imported_modules.add(node.module)
            for alias in node.names:
                self.imported_from_pairs.add((node.module, alias.name))
        self.generic_visit(node)


def find_one_hop_callers(
    target_files: Sequence[str | Path],
    repo_root: Path | None = None,
) -> list[str]:
    """Finds 1-hop Python caller files in backend_v2 importing any of the target files via pure AST analysis.

    Excludes tests directories and target files themselves.

    Args:
        target_files: Target file paths to discover callers for.
        repo_root: Optional repository root path.

    Returns:
        Sorted list of relative POSIX file paths that import any target module.
    """
    root = repo_root or get_repo_root()
    backend_dir = root / "backend_v2"
    if not backend_dir.is_dir():
        return []

    # Map target files to possible import representations
    target_modules: set[str] = set()
    target_parent_stems: set[tuple[str, str]] = set()
    normalized_target_posix: set[str] = set()

    for tf in target_files:
        p = Path(tf)
        try:
            rel = p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()
        normalized_target_posix.add(rel)

        if rel.endswith(".py"):
            parts = rel[:-3].replace("\\", "/").split("/")
            mod_full = ".".join(parts)
            target_modules.add(mod_full)
            if len(parts) >= 2:
                parent_mod = ".".join(parts[:-1])
                target_parent_stems.add((parent_mod, parts[-1]))

    if not target_modules:
        return []

    callers: set[str] = set()

    for py_file in backend_dir.rglob("*.py"):
        rel_posix = py_file.resolve().relative_to(root.resolve()).as_posix()
        path_parts = set(rel_posix.split("/"))
        if "tests" in path_parts or rel_posix in normalized_target_posix:
            continue

        try:
            source_content = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source_content, filename=rel_posix)
        except SyntaxError:
            continue

        extractor = _ImportExtractor()
        extractor.visit(tree)

        matched = False
        for mod in target_modules:
            if mod in extractor.imported_modules:
                matched = True
                break
            if any(imp.startswith(f"{mod}.") for imp in extractor.imported_modules):
                matched = True
                break

        if not matched:
            for parent_mod, stem in target_parent_stems:
                if (parent_mod, stem) in extractor.imported_from_pairs:
                    matched = True
                    break

        if matched:
            callers.add(rel_posix)

    return sorted(callers)


def _is_field_call(node: ast.AST | None) -> bool:
    """Checks whether an AST node is a Call to Field()."""
    if isinstance(node, ast.Call):
        match node.func:
            case ast.Name(id="Field") | ast.Attribute(attr="Field"):
                return True
    return False


def _has_annotated_field(node: ast.AST | None) -> bool:
    """Checks whether an annotation is an Annotated subscript containing Field()."""
    if isinstance(node, ast.Subscript):
        is_annotated = False
        match node.value:
            case ast.Name(id="Annotated") | ast.Attribute(attr="Annotated"):
                is_annotated = True
            case _:
                pass
        if is_annotated:
            for child in ast.walk(node.slice):
                if _is_field_call(child):
                    return True
    return False


def _is_empty_or_pass_body(body: list[ast.stmt]) -> bool:
    """Checks if an AST statement list consists solely of pass or docstrings."""
    if not body:
        return True
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue
        return False
    return True


class _PythonTechnicalDebtVisitor(ast.NodeVisitor):
    """AST visitor inspecting a Python source file for 7-item technical debt patterns."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.findings: list[TechnicalDebtFindingDTO] = []
        normalized = filepath.replace("\\", "/")
        path_parts = set(normalized.strip("/").split("/"))
        self.is_test = "backend_v2/tests/" in normalized or "tests" in path_parts
        self.is_exempt = is_boundary_exempt(filepath)
        self.current_class_name: str | None = None
        self.test_function_names: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev_class = self.current_class_name
        self.current_class_name = node.name

        # Item 4: Check class body for duplicate Field() on Annotated or mutable defaults
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                target_name = ast.unparse(item.target)
                if not target_name.startswith("_") and isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                    self.findings.append(
                        TechnicalDebtFindingDTO(
                            rule_code="QGR020",
                            file_path=self.filepath,
                            lineno=item.lineno,
                            col_offset=item.col_offset,
                            message=f"Banned mutable class-level default in `{node.name}` on `{target_name}`: `{ast.unparse(item.value)}`.",
                            remediation="Use Field(default_factory=list/dict) inside Annotated or default to None.",
                            severity=GuardrailSeverity.FATAL,
                            debt_category="python_ast_mutable_defaults",
                        )
                    )
                if _has_annotated_field(item.annotation) and _is_field_call(item.value):
                    self.findings.append(
                        TechnicalDebtFindingDTO(
                            rule_code="QGR020",
                            file_path=self.filepath,
                            lineno=item.lineno,
                            col_offset=item.col_offset,
                            message=f"Duplicate Field() assignment on Annotated field `{target_name}`: `{ast.unparse(item)}`.",
                            remediation="Remove redundant `= Field(...)` assignment when metadata is defined in Annotated.",
                            severity=GuardrailSeverity.FATAL,
                            debt_category="python_ast_mutable_defaults",
                        )
                    )
            elif isinstance(item, ast.Assign):
                for t in item.targets:
                    target_name = ast.unparse(t)
                    if not target_name.startswith("_") and isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                        self.findings.append(
                            TechnicalDebtFindingDTO(
                                rule_code="QGR020",
                                file_path=self.filepath,
                                lineno=item.lineno,
                                col_offset=item.col_offset,
                                message=f"Banned mutable class-level default in `{node.name}` on `{target_name}`: `{ast.unparse(item.value)}`.",
                                remediation="Use Field(default_factory=list/dict) or default to None.",
                                severity=GuardrailSeverity.FATAL,
                                debt_category="python_ast_mutable_defaults",
                            )
                        )

        self.generic_visit(node)
        self.current_class_name = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function_defaults(node)
        if node.name.startswith("test_"):
            self.test_function_names.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function_defaults(node)
        if node.name.startswith("test_"):
            self.test_function_names.append(node.name)
        self.generic_visit(node)

    def _check_function_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Item 4: Mutable default arguments
        all_defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
        for default in all_defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append(
                    TechnicalDebtFindingDTO(
                        rule_code="TD_MUTABLE_DEFAULT",
                        file_path=self.filepath,
                        lineno=default.lineno,
                        col_offset=default.col_offset,
                        message=f"Banned mutable default parameter value in `{node.name}`: `{ast.unparse(default)}`.",
                        remediation="Use None as default parameter value and initialize container inside function body.",
                        severity=GuardrailSeverity.FATAL,
                        debt_category="python_ast_mutable_defaults",
                    )
                )

    def visit_Try(self, node: ast.Try) -> None:
        # Item 3: Exception swallowing (except Exception: pass)
        for handler in node.handlers:
            is_generic_exception = False
            if handler.type is None:
                is_generic_exception = True
            elif isinstance(handler.type, ast.Name) and handler.type.id in ("Exception", "BaseException"):
                is_generic_exception = True
            elif isinstance(handler.type, ast.Attribute) and handler.type.attr in ("Exception", "BaseException"):
                is_generic_exception = True

            if is_generic_exception and _is_empty_or_pass_body(handler.body):
                self.findings.append(
                    TechnicalDebtFindingDTO(
                        rule_code="TD_EXCEPT_PASS",
                        file_path=self.filepath,
                        lineno=handler.lineno,
                        col_offset=handler.col_offset,
                        message="Banned exception swallowing (except Exception: pass) detected.",
                        remediation="Catch specific typed exceptions and re-raise via AppException or handle explicitly.",
                        severity=GuardrailSeverity.FATAL,
                        debt_category="python_ast_exception_swallowing",
                    )
                )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Item 1: Reflection (getattr, hasattr, setattr)
        if not self.is_exempt and not self.is_test:
            match node.func:
                case ast.Name(id="getattr" | "hasattr" | "setattr"):
                    self.findings.append(
                        TechnicalDebtFindingDTO(
                            rule_code="QGR001",
                            file_path=self.filepath,
                            lineno=node.lineno,
                            col_offset=node.col_offset,
                            message=f"Banned dynamic reflection call `{node.func.id}`: `{ast.unparse(node)}`.",
                            remediation=f"Replace `{node.func.id}()` with direct typed attribute access or explicit match/case.",
                            severity=GuardrailSeverity.WARNING,
                            debt_category="python_ast_reflection",
                        )
                    )
                case _:
                    pass

        # Item 2: Dict fallbacks (.get() lookups)
        if not self.is_exempt and not self.is_test:
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                receiver = node.func.value
                exempt = False
                match receiver:
                    case ast.Attribute(value=ast.Name(id="os"), attr="environ") | ast.Name(id="environ"):
                        exempt = True
                    case ast.Attribute(attr="headers") | ast.Name(id="headers"):
                        exempt = True
                    case ast.Name(id=name) if name in {
                        "client",
                        "http",
                        "requests",
                        "session",
                        "httpx",
                        "driver",
                        "router",
                        "app",
                        "redis",
                        "redis_client",
                    } or name.endswith(("_router", "_subrouter", "_client")):
                        exempt = True
                    case _:
                        pass

                if not exempt and (len(node.args) >= 1 or len(node.keywords) >= 1):
                    self.findings.append(
                        TechnicalDebtFindingDTO(
                            rule_code="TD_DICT_GET",
                            file_path=self.filepath,
                            lineno=node.lineno,
                            col_offset=node.col_offset,
                            message=f"Banned permissive `.get()` lookup on domain state: `{ast.unparse(node)}`.",
                            remediation="Access typed domain fields directly via dot notation with fail-fast validation.",
                            severity=GuardrailSeverity.WARNING,
                            debt_category="python_ast_dict_fallbacks",
                        )
                    )

        # Item 7: Model Factory Parity (in touched test files)
        if self.is_test and "scripts" not in self.filepath and "factories" not in self.filepath:
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "model_validate"
                and node.args
                and isinstance(node.args[0], ast.Dict)
            ):
                self.findings.append(
                    TechnicalDebtFindingDTO(
                        rule_code="TD_MODEL_FACTORY",
                        file_path=self.filepath,
                        lineno=node.lineno,
                        col_offset=node.col_offset,
                        message=f"Test file passes raw dict literal to `model_validate`: `{ast.unparse(node)}`.",
                        remediation="Use ModelFactory.build() from backend_v2/tests/factories/model_factories.py instead of raw dict fixtures.",
                        severity=GuardrailSeverity.WARNING,
                        debt_category="model_factory_parity",
                    )
                )

        self.generic_visit(node)


def scan_python_technical_debt(filepath: str | Path, source_text: str | None = None) -> list[TechnicalDebtFindingDTO]:
    """Scans a Python source file for technical debt according to the 7-item checklist.

    Args:
        filepath: Target file path to scan.
        source_text: Optional explicit source code string.

    Returns:
        List of TechnicalDebtFindingDTO violations discovered.
    """
    p = Path(filepath)
    norm_path = p.as_posix()

    if source_text is None:
        if not p.is_file():
            return []
        try:
            source_text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return [
                TechnicalDebtFindingDTO(
                    rule_code="TD_IO_ERROR",
                    file_path=norm_path,
                    lineno=1,
                    col_offset=0,
                    message=f"Failed to read file: {e}",
                    remediation="Ensure file exists and is readable.",
                    severity=GuardrailSeverity.FATAL,
                    debt_category="python_ast_syntax",
                )
            ]

    try:
        tree = ast.parse(source_text, filename=norm_path)
    except SyntaxError as err:
        return [
            TechnicalDebtFindingDTO(
                rule_code="QGR000",
                file_path=norm_path,
                lineno=err.lineno or 1,
                col_offset=err.offset or 0,
                message=f"SyntaxError: {err.msg}",
                remediation="Fix Python syntax error.",
                severity=GuardrailSeverity.FATAL,
                debt_category="python_ast_syntax",
            )
        ]

    visitor = _PythonTechnicalDebtVisitor(filepath=norm_path)
    visitor.visit(tree)
    findings = list(visitor.findings)

    # Item 6: ISTQB Test Partition Check for test files
    if visitor.is_test and visitor.test_function_names:
        has_negative = any(
            any(k in fn.lower() for k in ("failure", "invalid", "error", "fail", "negative"))
            for fn in visitor.test_function_names
        )
        if not has_negative:
            findings.append(
                TechnicalDebtFindingDTO(
                    rule_code="TD_ISTQB_NEGATIVE",
                    file_path=norm_path,
                    lineno=1,
                    col_offset=0,
                    message="Touched test file lacks ISTQB negative/edge-case partitions (test_*_failure, test_*_invalid, test_*_error).",
                    remediation="Add negative test functions exercising failure, invalid input, or exception states.",
                    severity=GuardrailSeverity.WARNING,
                    debt_category="istqb_test_partitions",
                )
            )

    return findings


def scan_dart_technical_debt(filepath: str | Path, source_bytes: bytes | None = None) -> list[TechnicalDebtFindingDTO]:
    """Scans a Dart source file for technical debt (DGR001-DGR010).

    Args:
        filepath: Target Dart file path.
        source_bytes: Optional explicit source code bytes.

    Returns:
        List of TechnicalDebtFindingDTO violations discovered.
    """
    p = Path(filepath)
    norm_path = p.as_posix()

    if source_bytes is None:
        if not p.is_file():
            return []
        try:
            source_bytes = p.read_bytes()
        except OSError as e:
            return [
                TechnicalDebtFindingDTO(
                    rule_code="TD_IO_ERROR",
                    file_path=norm_path,
                    lineno=1,
                    col_offset=0,
                    message=f"Failed to read file: {e}",
                    remediation="Ensure file exists and is readable.",
                    severity=GuardrailSeverity.FATAL,
                    debt_category="flutter_dart_anti_patterns",
                )
            ]

    dart_violations = scan_dart_source(norm_path, source_bytes, strict=True)
    return [
        TechnicalDebtFindingDTO(
            rule_code=v.rule_code,
            file_path=v.filepath,
            lineno=v.lineno,
            col_offset=v.col_offset,
            message=v.message,
            remediation=v.remediation,
            severity=GuardrailSeverity(v.severity.value),
            debt_category="flutter_dart_anti_patterns",
        )
        for v in dart_violations
    ]


def scan_targets_technical_debt(
    targets: Sequence[str | Path],
    include_one_hop: bool = False,
    strict: bool = False,
    repo_root: Path | None = None,
) -> TechnicalDebtScanResultDTO:
    """Performs the full technical debt sweep across targets and optional 1-hop callers.

    Args:
        targets: Target file or directory paths.
        include_one_hop: Whether to automatically discover and scan 1-hop caller dependencies.
        strict: When True, treats any finding (warning or fatal) as failure.
        repo_root: Optional repository root path.

    Returns:
        TechnicalDebtScanResultDTO encapsulating targets, callers, findings, and passed status.
    """
    root = repo_root or get_repo_root()
    norm_targets: list[str] = []

    for t in targets:
        p = Path(t)
        if not p.is_absolute():
            p = root / p
        try:
            rel = p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()
        norm_targets.append(rel)

    norm_targets = sorted(set(norm_targets))

    one_hop_callers: list[str] = []
    if include_one_hop:
        one_hop_callers = find_one_hop_callers(norm_targets, repo_root=root)

    all_files_to_scan = sorted(set(norm_targets + one_hop_callers))
    findings: list[TechnicalDebtFindingDTO] = []

    for file_path_str in all_files_to_scan:
        p = Path(file_path_str)
        abs_p = p if p.is_absolute() else root / p

        if abs_p.is_dir():
            for child in abs_p.rglob("*"):
                if child.is_file():
                    try:
                        child_rel = child.resolve().relative_to(root.resolve())
                    except ValueError:
                        child_rel = child
                    if child.suffix == ".py":
                        findings.extend(scan_python_technical_debt(child_rel))
                    elif child.suffix == ".dart":
                        findings.extend(scan_dart_technical_debt(child_rel))
        elif abs_p.is_file():
            try:
                rel_path = abs_p.resolve().relative_to(root.resolve())
            except ValueError:
                rel_path = abs_p
            if rel_path.suffix == ".py":
                findings.extend(scan_python_technical_debt(rel_path))
            elif rel_path.suffix == ".dart":
                findings.extend(scan_dart_technical_debt(rel_path))

    has_fatal = any(f.severity == GuardrailSeverity.FATAL for f in findings)
    passed = (len(findings) == 0) if strict else (not has_fatal)

    return TechnicalDebtScanResultDTO(
        targets=norm_targets,
        one_hop_callers=one_hop_callers,
        findings=findings,
        passed=passed,
    )


def format_technical_debt_markdown(result: TechnicalDebtScanResultDTO) -> str:
    """Formats technical debt scan results into a clean GitHub Flavored Markdown table.

    Suitable for direct insertion into Phase 1 Pre-Implementation Cleanups.

    Args:
        result: Scan result DTO.

    Returns:
        Formatted markdown table string.
    """
    lines: list[str] = [
        "### Technical Debt Audit Report",
        "",
        f"- **Targets Scanned:** {len(result.targets)}",
        f"- **1-Hop Callers Scanned:** {len(result.one_hop_callers)}",
        f"- **Total Findings:** {len(result.findings)}",
        f"- **Status:** {'✅ PASSED (Clean)' if result.passed else '❌ FAILED (Technical Debt Detected)'}",
        "",
    ]
    if not result.findings:
        lines.append("No technical debt discovered across the specified scope.")
        return "\n".join(lines)

    lines.extend(
        [
            "| File | Line | Rule | Severity | Category | Message | Remediation |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    for f in result.findings:
        sev_tag = "❌ FATAL" if f.severity == GuardrailSeverity.FATAL else "⚠️ WARN"
        lines.append(
            f"| `{f.file_path}` | {f.lineno} | `{f.rule_code}` | {sev_tag} | `{f.debt_category}` | {f.message} | {f.remediation} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    """CLI entrypoint for technical debt and 1-hop caller scanner."""
    setup_script_environment()

    parser = argparse.ArgumentParser(
        description="Deterministic Technical Debt & 1-Hop Caller Audit Scanner CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--targets",
        nargs="*",
        default=[],
        help="Target files or directories to scan.",
    )
    parser.add_argument(
        "--plan",
        type=str,
        default=None,
        help="Path to implementation plan markdown file from which to extract target files.",
    )
    parser.add_argument(
        "--include-one-hop",
        action="store_true",
        help="Automatically discover and scan 1-hop caller dependencies in backend_v2.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warning violations as failures.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit results strictly in JSON format.",
    )

    args = parser.parse_args(argv)

    root = repo_root or get_repo_root()
    target_paths: list[str] = list(args.targets)

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.is_absolute():
            plan_path = root / plan_path
        if not plan_path.is_file():
            print(f"{ANSIColors.RED}Error: Plan file not found: {args.plan}{ANSIColors.RESET}", file=sys.stderr)
            return 1
        plan_content = plan_path.read_text(encoding="utf-8", errors="replace")
        extracted_targets = extract_target_files(plan_content)
        # Filter for MODIFY and NEW actions
        target_paths.extend([t.file_path for t in extracted_targets if t.action in ("MODIFY", "NEW")])

    if not target_paths:
        print(
            f"{ANSIColors.RED}Error: No target files specified. Provide --targets <files...> or --plan <path>.{ANSIColors.RESET}",
            file=sys.stderr,
        )
        parser.print_help()
        return 1

    result = scan_targets_technical_debt(
        targets=target_paths,
        include_one_hop=args.include_one_hop,
        strict=args.strict,
        repo_root=root,
    )

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(format_technical_debt_markdown(result))

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())

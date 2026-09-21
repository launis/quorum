"""Deterministic AST Multi-Layer Dict Eradication Auditor.

Statically analyzes backend Python files to mathematically verify:
1. Exactly 0 naked dict[str, Any] / dict[str, object] type annotations.
2. Exactly 0 isinstance(..., dict) checks in domain and service layers.
3. Exactly 0 unauthorized/unjustified # noqa: QGR suppressions.
4. Exactly 0 imports or references to legacy dict_utils.
5. Exactly 0 syntax/AST parse errors across the scanned scope.
6. Exactly 0 unexempt .get() calls in domain, service, hook, and worker layers.
7. Exactly 0 dynamic reflection calls (getattr, hasattr, setattr) in domain layers.
8. Exactly 0 Primitive Obsession nested dictionary annotations (dict[..., dict[...]]).
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "AuditViolation",
    "DictEradicationReport",
    "DictEradicationVisitor",
    "audit_dict_eradication",
    "audit_file_comments",
    "main",
]

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
    """Represents a discovered audit violation.

    Attributes:
        filepath: Target file path where the violation was discovered.
        line: Line number where the violation occurred.
        metric: Metric category name.
        message: Descriptive violation message.
    """

    filepath: str
    line: int
    metric: str
    message: str


@dataclass
class DictEradicationReport:
    """Aggregated audit report across all mathematical metrics.

    Attributes:
        naked_dict_annotations: Count of naked dict annotations found.
        service_duck_typing: Count of service duck typing occurrences.
        unauthorized_suppressions: Count of unauthorized suppressions.
        dict_utils_references: Count of legacy dict_utils references.
        syntax_parse_errors: Count of syntax parse errors.
        banned_get_calls: Count of banned internal get calls.
        reflection_calls: Count of reflection calls.
        primitive_obsession_nested_dicts: Count of primitive obsession nested dicts.
        violations: List of discovered audit violations.
    """

    naked_dict_annotations: int = 0
    service_duck_typing: int = 0
    unauthorized_suppressions: int = 0
    dict_utils_references: int = 0
    syntax_parse_errors: int = 0
    banned_get_calls: int = 0
    reflection_calls: int = 0
    primitive_obsession_nested_dicts: int = 0
    violations: list[AuditViolation] = field(default_factory=list)

    @property
    def total_violations(self) -> int:
        """Returns the total number of violations across all metrics."""
        return (
            self.naked_dict_annotations
            + self.service_duck_typing
            + self.unauthorized_suppressions
            + self.dict_utils_references
            + self.syntax_parse_errors
            + self.banned_get_calls
            + self.reflection_calls
            + self.primitive_obsession_nested_dicts
        )


class DictEradicationVisitor(ast.NodeVisitor):
    """AST Visitor scanning Python files for permissive dict and reflection patterns."""

    def __init__(self, filepath: str, source_bytes: bytes) -> None:
        """Initialize the visitor with target file path and source bytes.

        Args:
            filepath: Target file path to scan.
            source_bytes: Source code content in bytes.
        """
        self.filepath = filepath
        self.source_bytes = source_bytes
        self.filename = Path(filepath).name
        self.is_exempt = self.filename in LOCKED_PHYSICAL_DRIVERS
        self.is_test = "tests" in Path(filepath).parts
        self.is_domain_or_service = any(
            p in Path(filepath).parts
            for p in ("services", "models", "hooks", "orchestrator", "api", "database", "workers")
        )
        self.violations: list[AuditViolation] = []

    def _is_naked_dict_subscript(self, node: ast.AST) -> bool:
        """Checks whether an AST node contains a subscript of dict[..., Any/object].

        Args:
            node: AST node to inspect.

        Returns:
            True if a naked dict subscript is present, False otherwise.
        """
        for target in ast.walk(node):
            if isinstance(target, ast.Subscript):
                is_dict_type = False
                match target.value:
                    case ast.Name(id="dict" | "Dict") | ast.Attribute(attr="dict" | "Dict"):
                        is_dict_type = True
                    case _:
                        is_dict_type = False

                if is_dict_type:
                    match target.slice:
                        case ast.Tuple(elts=elements) if len(elements) == 2:
                            val_type = elements[1]
                            match val_type:
                                case ast.Name(id="Any" | "object") | ast.Attribute(attr="Any" | "object"):
                                    return True
                                case _:
                                    pass
                        case ast.Name(id="Any" | "object") | ast.Attribute(attr="Any" | "object"):
                            return True
                        case _:
                            pass
        return False

    def _find_nested_dict_subscript(self, node: ast.AST | None) -> ast.Subscript | None:
        """Finds any nested dictionary or primitive collection obsession annotation in the AST node.

        Args:
            node: AST node or None to inspect.

        Returns:
            The offending Subscript node if a nested dict or collection is found, None otherwise.
        """
        if node is None:
            return None
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Subscript):
                continue

            # Pattern 1: Outer dict with inner dict or collection of dicts
            is_outer_dict = False
            match sub.value:
                case ast.Name(id="dict" | "Dict") | ast.Attribute(attr="dict" | "Dict"):
                    is_outer_dict = True
                case _:
                    pass
            if is_outer_dict:
                match sub.slice:
                    case ast.Tuple(elts=elements) if len(elements) == 2:
                        val_type = elements[1]
                        for inner in ast.walk(val_type):
                            if inner is val_type and isinstance(inner, ast.Name) and inner.id in ("dict", "Dict"):
                                return sub
                            if isinstance(inner, ast.Subscript):
                                match inner.value:
                                    case ast.Name(id="dict" | "Dict") | ast.Attribute(attr="dict" | "Dict"):
                                        return sub
                                    case _:
                                        pass
                    case _:
                        pass

            # Pattern 2: Outer collection (list, List, Sequence, Iterable, set, Set) containing dict
            is_outer_collection = False
            match sub.value:
                case (
                    ast.Name(id="list" | "List" | "Sequence" | "Iterable" | "set" | "Set")
                    | ast.Attribute(attr="list" | "List" | "Sequence" | "Iterable" | "set" | "Set")
                ):
                    is_outer_collection = True
                case _:
                    pass
            if is_outer_collection:
                for inner in ast.walk(sub.slice):
                    if isinstance(inner, ast.Subscript):
                        match inner.value:
                            case ast.Name(id="dict" | "Dict") | ast.Attribute(attr="dict" | "Dict"):
                                return sub
                            case _:
                                pass
                    elif isinstance(inner, ast.Name) and inner.id in ("dict", "Dict"):
                        return sub
                    elif isinstance(inner, ast.Attribute) and inner.attr in ("dict", "Dict"):
                        return sub
        return None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Inspects variable type annotations for naked dicts and primitive obsession nested dicts.

        Args:
            node: AnnAssign node to inspect.
        """
        if not self.is_exempt and not self.is_test:
            if self._is_naked_dict_subscript(node.annotation):
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="naked_dict_annotations",
                        message=f"Naked dict annotation found: `{ast.unparse(node.annotation)}`",
                    )
                )
            if self._find_nested_dict_subscript(node.annotation) is not None:
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="primitive_obsession_nested_dicts",
                        message=(
                            f"Primitive Obsession nested dict annotation found: `{ast.unparse(node.annotation)}`. "
                            "Encapsulate inner dictionary in a typed Pydantic V2 DTO."
                        ),
                    )
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Inspects function parameter and return type annotations.

        Args:
            node: FunctionDef node to inspect.
        """
        if not self.is_exempt and not self.is_test:
            if node.returns is not None:
                if self._is_naked_dict_subscript(node.returns):
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=node.lineno,
                            metric="naked_dict_annotations",
                            message=(
                                f"Naked dict return type annotation in `{node.name}`: `{ast.unparse(node.returns)}`"
                            ),
                        )
                    )
                if self._find_nested_dict_subscript(node.returns) is not None:
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=node.lineno,
                            metric="primitive_obsession_nested_dicts",
                            message=(
                                f"Primitive Obsession nested dict return type in `{node.name}`: "
                                f"`{ast.unparse(node.returns)}`. "
                                "Encapsulate inner dictionary in a typed Pydantic V2 DTO."
                            ),
                        )
                    )

            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            for arg in all_args:
                if arg.annotation is not None:
                    if self._is_naked_dict_subscript(arg.annotation):
                        self.violations.append(
                            AuditViolation(
                                filepath=self.filepath,
                                line=arg.lineno,
                                metric="naked_dict_annotations",
                                message=(
                                    f"Naked dict argument annotation for `{arg.arg}` in `{node.name}`: "
                                    f"`{ast.unparse(arg.annotation)}`"
                                ),
                            )
                        )
                    if self._find_nested_dict_subscript(arg.annotation) is not None:
                        self.violations.append(
                            AuditViolation(
                                filepath=self.filepath,
                                line=arg.lineno,
                                metric="primitive_obsession_nested_dicts",
                                message=(
                                    f"Primitive Obsession nested dict argument for `{arg.arg}` in `{node.name}`: "
                                    f"`{ast.unparse(arg.annotation)}`. "
                                    "Encapsulate inner dictionary in a typed Pydantic V2 DTO."
                                ),
                            )
                        )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Inspects async function parameter and return type annotations.

        Args:
            node: AsyncFunctionDef node to inspect.
        """
        if not self.is_exempt and not self.is_test:
            if node.returns is not None:
                if self._is_naked_dict_subscript(node.returns):
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=node.lineno,
                            metric="naked_dict_annotations",
                            message=(
                                f"Naked dict return type annotation in async `{node.name}`: "
                                f"`{ast.unparse(node.returns)}`"
                            ),
                        )
                    )
                if self._find_nested_dict_subscript(node.returns) is not None:
                    self.violations.append(
                        AuditViolation(
                            filepath=self.filepath,
                            line=node.lineno,
                            metric="primitive_obsession_nested_dicts",
                            message=(
                                f"Primitive Obsession nested dict return type in async `{node.name}`: "
                                f"`{ast.unparse(node.returns)}`. "
                                "Encapsulate inner dictionary in a typed Pydantic V2 DTO."
                            ),
                        )
                    )

            all_args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            for arg in all_args:
                if arg.annotation is not None:
                    if self._is_naked_dict_subscript(arg.annotation):
                        self.violations.append(
                            AuditViolation(
                                filepath=self.filepath,
                                line=arg.lineno,
                                metric="naked_dict_annotations",
                                message=(
                                    f"Naked dict argument annotation for `{arg.arg}` in async `{node.name}`: "
                                    f"`{ast.unparse(arg.annotation)}`"
                                ),
                            )
                        )
                    if self._find_nested_dict_subscript(arg.annotation) is not None:
                        self.violations.append(
                            AuditViolation(
                                filepath=self.filepath,
                                line=arg.lineno,
                                metric="primitive_obsession_nested_dicts",
                                message=(
                                    f"Primitive Obsession nested dict argument for `{arg.arg}` in async `{node.name}`: "
                                    f"`{ast.unparse(arg.annotation)}`. "
                                    "Encapsulate inner dictionary in a typed Pydantic V2 DTO."
                                ),
                            )
                        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Inspects isinstance calls, reflection, and banned .get() lookups.

        Args:
            node: Call node to inspect.
        """
        if not self.is_exempt and not self.is_test and self.is_domain_or_service:
            # 1. Banned isinstance duck-typing
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

            # 2. Banned dynamic reflection
            if isinstance(node.func, ast.Name) and node.func.id in {"getattr", "hasattr", "setattr", "vars"}:
                self.violations.append(
                    AuditViolation(
                        filepath=self.filepath,
                        line=node.lineno,
                        metric="reflection_calls",
                        message=f"Banned dynamic reflection call `{node.func.id}`: `{ast.unparse(node)}`",
                    )
                )

            # 3. Banned .get() lookups on internal state / variables
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                if len(node.args) == 0 and not any(
                    kw.arg not in {"params", "headers", "timeout", "auth", "cookies"} for kw in node.keywords
                ):
                    pass
                else:
                    exempt = False
                    receiver = node.func.value
                    match receiver:
                        case ast.Attribute(value=ast.Name(id="os"), attr="environ") | ast.Name(id="environ"):
                            exempt = True
                        case ast.Attribute(attr="headers") | ast.Name(id="headers"):
                            exempt = True
                        case (
                            ast.Name(
                                id="client"
                                | "http"
                                | "requests"
                                | "session"
                                | "httpx"
                                | "driver"
                                | "_LABEL_MAP"
                                | "LABEL_MAP"
                                | "_VALUE_MAP"
                                | "_NAME_MAP"
                                | "_L10N_MAP"
                                | "L10N_MAP"
                            )
                            | ast.Attribute(
                                attr="client"
                                | "http"
                                | "requests"
                                | "session"
                                | "httpx"
                                | "driver"
                                | "_LABEL_MAP"
                                | "LABEL_MAP"
                                | "_VALUE_MAP"
                                | "_NAME_MAP"
                                | "_L10N_MAP"
                                | "L10N_MAP"
                            )
                        ):
                            exempt = True
                        case _:
                            exempt = False

                    if not exempt:
                        for kw in node.keywords:
                            if kw.arg in {"params", "headers", "timeout", "auth", "cookies"}:
                                exempt = True
                                break

                    if not exempt:
                        self.violations.append(
                            AuditViolation(
                                filepath=self.filepath,
                                line=node.lineno,
                                metric="banned_get_calls",
                                message=f"Banned .get() lookup on internal state/variable: `{ast.unparse(node)}`",
                            )
                        )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Inspects imports for dict_utils references.

        Args:
            node: Import node to inspect.
        """
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
        """Inspects from imports for dict_utils references.

        Args:
            node: ImportFrom node to inspect.
        """
        has_dict_utils = False
        if node.module and "dict_utils" in node.module:
            has_dict_utils = True
        elif any("dict_utils" in alias.name for alias in node.names):
            has_dict_utils = True

        if has_dict_utils:
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
    """Audits comments in a file to verify all # noqa: QGR suppressions have substantive reasons.

    Args:
        filepath: Target file path of the source code.
        source_bytes: Raw source content bytes.

    Returns:
        List of discovered comment audit violations.
    """
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
    except (tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError) as e:
        violations.append(
            AuditViolation(
                filepath=filepath,
                line=1,
                metric="syntax_parse_error",
                message=f"Failed to tokenize file comments: {e}",
            )
        )
    return violations


def audit_dict_eradication(
    targets: Path | str | Sequence[Path | str] = "backend_v2",
) -> DictEradicationReport:
    """Executes the complete multi-layer dict eradication audit on target directory or files.

    Args:
        targets: Directory or sequence of files/directories to audit.

    Returns:
        DictEradicationReport containing metrics and discovered violations.
    """
    report = DictEradicationReport()

    target_list: list[Path] = []
    if isinstance(targets, (str, Path)):
        p = Path(targets)
        if p.is_dir():
            target_list.extend(sorted(p.rglob("*.py")))
        elif p.is_file():
            target_list.append(p)
        elif not p.exists():
            return report
    else:
        for t in targets:
            p = Path(t)
            if p.is_dir():
                target_list.extend(sorted(p.rglob("*.py")))
            elif p.is_file():
                target_list.append(p)

    for file_path in target_list:
        try:
            source_bytes = file_path.read_bytes()
            source_text = source_bytes.decode("utf-8")
            tree = ast.parse(source_text, filename=str(file_path))
        except (SyntaxError, IndentationError, UnicodeDecodeError) as e:
            report.syntax_parse_errors += 1
            line_no = e.lineno if isinstance(e, (SyntaxError, IndentationError)) and e.lineno is not None else 1
            report.violations.append(
                AuditViolation(
                    filepath=str(file_path),
                    line=line_no,
                    metric="syntax_parse_error",
                    message=f"Failed to parse AST: {e}",
                )
            )
            continue

        visitor = DictEradicationVisitor(str(file_path), source_bytes)
        visitor.visit(tree)

        for v in visitor.violations:
            if v.metric == "naked_dict_annotations":
                report.naked_dict_annotations += 1
            elif v.metric == "primitive_obsession_nested_dicts":
                report.primitive_obsession_nested_dicts += 1
            elif v.metric == "service_duck_typing":
                report.service_duck_typing += 1
            elif v.metric == "dict_utils_references":
                report.dict_utils_references += 1
            elif v.metric == "banned_get_calls":
                report.banned_get_calls += 1
            elif v.metric == "reflection_calls":
                report.reflection_calls += 1
            elif v.metric == "syntax_parse_error":
                report.syntax_parse_errors += 1
            report.violations.append(v)

        comment_violations = audit_file_comments(str(file_path), source_bytes)
        for cv in comment_violations:
            if cv.metric == "syntax_parse_error":
                report.syntax_parse_errors += 1
            else:
                report.unauthorized_suppressions += 1
            report.violations.append(cv)

    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for deterministic AST dict eradication audit.

    Args:
        argv: Optional command line arguments list.

    Returns:
        0 if all metrics pass with zero violations, 1 otherwise.
    """
    if isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError, io.UnsupportedOperation:
            pass

    print("=" * 80)
    print("  QUORUM DETERMINISTIC AST DICT ERADICATION AUDITOR")
    print("=" * 80)

    args = argv if argv is not None else sys.argv[1:]
    target = args if args else "backend_v2"
    report = audit_dict_eradication(target)

    print(f"1. Naked Dict Annotations (dict[str, Any]):     {report.naked_dict_annotations}")
    print(f"2. Primitive Obsession (Nested dict[..., dict]): {report.primitive_obsession_nested_dicts}")
    print(f"3. Service Layer Duck-Typing (isinstance):      {report.service_duck_typing}")
    print(f"4. Unauthorized # noqa Suppressions:            {report.unauthorized_suppressions}")
    print(f"5. Legacy dict_utils References:                {report.dict_utils_references}")
    print(f"6. Syntax/AST Parse Errors:                     {report.syntax_parse_errors}")
    print(f"7. Banned Internal .get() Calls:                {report.banned_get_calls}")
    print(f"8. Dynamic Reflection Calls:                    {report.reflection_calls}")
    print("-" * 80)
    print(f"TOTAL VIOLATIONS:                               {report.total_violations}")
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

    print("\n[PASSED] 100% Mathematical Zero Violations across all metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

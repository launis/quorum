"""Audit Markdown Boundaries.

Scans Markdown documents to ensure references, boundaries, and terminology
comply with the architectural standards. Emits structured Pydantic V2 DTOs
with deterministic remediation guidance.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

# ANSI colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class GuardrailSeverity(StrEnum):
    """Severity classification for markdown audit findings."""

    WARNING = "WARNING"
    FATAL = "FATAL"


class MarkdownAuditFinding(BaseModel):
    """Pydantic V2 DTO representing an architectural markdown boundary violation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    line_number: Annotated[int, Field(ge=0, description="1-indexed line number where violation occurred")]
    rule_code: Annotated[str, Field(pattern=r"^MBD\d{3}$", description="Rule code e.g. MBD001")]
    category: Annotated[str, Field(description="Category of finding")]
    message: Annotated[str, Field(description="Descriptive message")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    remediation: Annotated[str, Field(description="Deterministic remediation guidance")]


def print_error(msg: str) -> None:
    """Print an error message in red."""
    print(f"{RED}ERROR: {msg}{RESET}")


def print_success(msg: str) -> None:
    """Print a success message in green."""
    print(f"{GREEN}SUCCESS: {msg}{RESET}")


class MarkdownAuditor:
    """Auditor for analyzing architectural boundaries in Markdown."""

    def __init__(self, file_path: str, repo_root: str) -> None:
        """Initialize the auditor.

        Args:
            file_path: The file to audit.
            repo_root: The root of the repository.
        """
        self.file_path = file_path
        self.repo_root = Path(repo_root)
        with open(file_path, encoding="utf-8") as f:
            self.content = f.read()
        self.lines = self.content.splitlines()
        self.findings: list[MarkdownAuditFinding] = []

    @property
    def errors(self) -> list[str]:
        """Backward-compatible list of error message strings."""
        result: list[str] = []
        for f in self.findings:
            if f.line_number > 0:
                result.append(f"Line {f.line_number}: {f.message}")
            else:
                result.append(f.message)
        return result

    def _add_finding(
        self,
        line_number: int,
        rule_code: str,
        category: str,
        message: str,
        severity: GuardrailSeverity,
        remediation: str,
    ) -> None:
        """Add a structured finding to accumulated findings."""
        self.findings.append(
            MarkdownAuditFinding(
                line_number=line_number,
                rule_code=rule_code,
                category=category,
                message=message,
                severity=severity,
                remediation=remediation,
            )
        )

    def run_all_checks(self, exit_on_completion: bool = True) -> list[MarkdownAuditFinding]:
        """Run all verification checks on the markdown content.

        Args:
            exit_on_completion: If True, calls sys.exit based on audit outcome.

        Returns:
            List of MarkdownAuditFinding objects.
        """
        self.check_ambiguity()
        self.check_xml_truncation()
        self.check_file_references_and_ast_bounds()
        self.check_class_hallucinations()
        self.check_settings_validation()
        self.check_enum_validation()

        if exit_on_completion:
            if self.findings:
                print(f"\n{RED}Audit failed with {len(self.findings)} findings:{RESET}")
                for f in self.findings:
                    prefix = f"Line {f.line_number}: " if f.line_number > 0 else ""
                    color = RED if f.severity == GuardrailSeverity.FATAL else YELLOW
                    print(f"  - {color}[{f.rule_code}] ({f.severity}) {prefix}{f.message}{RESET}")
                    print(f"    Remediation: {f.remediation}")
                sys.exit(1)
            else:
                print_success(f"Audit passed for {self.file_path}")
                sys.exit(0)

        return self.findings

    def check_ambiguity(self) -> None:
        """Scan for ambiguous terminology that should be avoided."""
        pattern = re.compile(r"(?:\b|\s)(e\.g\.|etc\.|such as|like)(?:\s|$|[,.])", re.IGNORECASE)
        for i, line in enumerate(self.lines):
            match = pattern.search(line)
            if match:
                self._add_finding(
                    line_number=i + 1,
                    rule_code="MBD001",
                    category="Ambiguity",
                    message=f"Ambiguous language detected '{match.group(1)}'. Use programmatic SSOT references.",
                    severity=GuardrailSeverity.WARNING,
                    remediation="Replace ambiguous language with programmatic SSOT references or exhaustive concrete lists.",
                )

    def check_xml_truncation(self) -> None:
        """Verify that specific XML tags are correctly matched and not truncated."""
        tag_pattern = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9_]+)[^>]*>")
        stack: list[tuple[str, int]] = []
        for i, line in enumerate(self.lines):
            for match in tag_pattern.finditer(line):
                is_closing = match.group(1) == "/"
                tag_name = match.group(2)

                if tag_name not in ("execution_protocol", "step"):
                    continue

                if not is_closing:
                    stack.append((tag_name, i + 1))
                else:
                    if not stack:
                        self._add_finding(
                            line_number=i + 1,
                            rule_code="MBD002",
                            category="XML Truncation",
                            message=f"Closing tag </{tag_name}> without opening tag.",
                            severity=GuardrailSeverity.FATAL,
                            remediation="Ensure every closing XML tag has a corresponding opening tag.",
                        )
                    else:
                        top_tag, top_line = stack.pop()
                        if top_tag != tag_name:
                            self._add_finding(
                                line_number=i + 1,
                                rule_code="MBD002",
                                category="XML Truncation",
                                message=f"Mismatched closing tag </{tag_name}>. Expected </{top_tag}> from line {top_line}.",
                                severity=GuardrailSeverity.FATAL,
                                remediation=f"Fix tag nesting: replace </{tag_name}> with </{top_tag}> or reorder tags.",
                            )

        for tag_name, line_num in stack:
            self._add_finding(
                line_number=line_num,
                rule_code="MBD002",
                category="XML Truncation",
                message=f"Unclosed tag <{tag_name}>.",
                severity=GuardrailSeverity.FATAL,
                remediation=f"Add closing </{tag_name}> tag at the appropriate boundary.",
            )

    def check_file_references_and_ast_bounds(self) -> None:
        """Check all file references with line boundaries against the AST."""
        pattern = re.compile(r"@\[([^#\]]+)(?:#L(\d+)-L?(\d+))?\]")
        for i, line in enumerate(self.lines):
            for match in pattern.finditer(line):
                rel_path = match.group(1).strip()
                start_line = match.group(2)
                end_line = match.group(3)

                full_path = self.repo_root / rel_path

                if "[NEW]" in line or "[DELETE]" in line:
                    continue

                if rel_path.startswith("ki_") and rel_path.endswith(".md"):
                    continue

                if not full_path.exists():
                    self._add_finding(
                        line_number=i + 1,
                        rule_code="MBD003",
                        category="Missing File",
                        message=f"Referenced file does not exist: {rel_path}",
                        severity=GuardrailSeverity.FATAL,
                        remediation="Verify referenced relative file path exists in repository or mark as [NEW] if planned.",
                    )
                    continue

                if start_line and end_line and full_path.suffix == ".py":
                    self.verify_ast_bounds(full_path, int(start_line), int(end_line), i + 1, rel_path)

    def verify_ast_bounds(
        self, file_path: Path, start_line: int, end_line: int, md_line_num: int, rel_path: str
    ) -> None:
        """Verify that line ranges match a class or function definition exactly without reflection."""
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=file_path.as_posix())
        except SyntaxError:
            self._add_finding(
                line_number=md_line_num,
                rule_code="MBD004",
                category="AST Bound Error",
                message=f"SyntaxError parsing {rel_path} for AST bounding.",
                severity=GuardrailSeverity.FATAL,
                remediation="Fix Python syntax error in referenced file so AST bounds can be parsed.",
            )
            return
        except (OSError, UnicodeDecodeError) as e:
            self._add_finding(
                line_number=md_line_num,
                rule_code="MBD004",
                category="AST Bound Error",
                message=f"Error reading {rel_path} for AST bounding: {e}",
                severity=GuardrailSeverity.FATAL,
                remediation="Ensure referenced file is readable with UTF-8 encoding.",
            )
            return

        valid_bounds: list[tuple[int, int]] = []
        for node in ast.walk(tree):
            match node:
                case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                    node_start = (
                        min((d.lineno for d in node.decorator_list), default=node.lineno)
                        if node.decorator_list
                        else node.lineno
                    )
                    node_end = node.end_lineno if node.end_lineno is not None else node.lineno
                    valid_bounds.append((node_start, node_end))
                case _:
                    pass

        if (start_line, end_line) not in valid_bounds:
            self._add_finding(
                line_number=md_line_num,
                rule_code="MBD004",
                category="AST Bound Mismatch",
                message=f"AST Bound mismatch for {rel_path}#L{start_line}-L{end_line}. No exact Class/Function matches these lines.",
                severity=GuardrailSeverity.FATAL,
                remediation="Update line bounds to match exact ClassDef, FunctionDef, or AsyncFunctionDef node spans.",
            )

    def check_class_hallucinations(self) -> None:
        """Scan mentioned DTOs/Classes and ensure they exist in backend_v2."""
        pattern = re.compile(r"`([A-Za-z0-9_]+(?:DTO|Cache|Response|Service))`")
        mentioned = set(pattern.findall(self.content))
        if not mentioned:
            return

        valid_classes: set[str] = set()
        backend_dir = self.repo_root / "backend_v2"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    source = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(source, filename=py_file.as_posix())
                    for node in ast.walk(tree):
                        match node:
                            case ast.ClassDef(name=class_name):
                                valid_classes.add(class_name)
                            case _:
                                pass
                except (OSError, UnicodeDecodeError, SyntaxError) as e:
                    self._add_finding(
                        line_number=0,
                        rule_code="MBD005",
                        category="Class Hallucination",
                        message=f"Failed to parse {py_file.as_posix()} for valid classes: {e}",
                        severity=GuardrailSeverity.WARNING,
                        remediation="Ensure all Python files in backend_v2 are syntactically valid.",
                    )

        for cls in sorted(mentioned):
            if cls not in valid_classes:
                self._add_finding(
                    line_number=0,
                    rule_code="MBD005",
                    category="Class Hallucination",
                    message=f"Class Hallucination: '{cls}' mentioned but not found in backend_v2.",
                    severity=GuardrailSeverity.WARNING,
                    remediation=f"Ensure '{cls}' exists in backend_v2/models/ or backend_v2/services/ or is defined in the plan.",
                )

    def check_settings_validation(self) -> None:
        """Validate references to backend settings.py."""
        pattern = re.compile(r"\bsettings\.([a-zA-Z0-9_]+)\b")
        mentioned = {m for m in pattern.findall(self.content) if m != "py"}
        if not mentioned:
            return

        settings_path = self.repo_root / "backend_v2" / "settings.py"
        valid_settings: set[str] = set()
        if settings_path.exists():
            try:
                tree = ast.parse(settings_path.read_text(encoding="utf-8"), filename=settings_path.as_posix())
                for node in ast.walk(tree):
                    match node:
                        case ast.ClassDef(name="Settings", body=body_items):
                            for item in body_items:
                                match item:
                                    case ast.AnnAssign(target=ast.Name(id=setting_id)):
                                        valid_settings.add(setting_id)
                                    case ast.Assign(targets=targets):
                                        for target in targets:
                                            match target:
                                                case ast.Name(id=setting_id):
                                                    valid_settings.add(setting_id)
                                                case _:
                                                    pass
                                    case _:
                                        pass
                        case _:
                            pass
            except (OSError, UnicodeDecodeError, SyntaxError) as e:
                self._add_finding(
                    line_number=0,
                    rule_code="MBD006",
                    category="Settings Hallucination",
                    message=f"Failed to parse {settings_path.as_posix()} for valid settings: {e}",
                    severity=GuardrailSeverity.WARNING,
                    remediation="Ensure backend_v2/settings.py contains a valid Settings ClassDef.",
                )

        for setting in sorted(mentioned):
            if setting not in valid_settings:
                self._add_finding(
                    line_number=0,
                    rule_code="MBD006",
                    category="Settings Hallucination",
                    message=f"Settings Hallucination: 'settings.{setting}' not found in backend_v2/settings.py.",
                    severity=GuardrailSeverity.WARNING,
                    remediation=f"Add '{setting}' to Settings model in backend_v2/settings.py or correct the reference.",
                )

    def check_enum_validation(self) -> None:
        """Validate references to Enums in backend and flutter models."""
        valid_enums: set[str] = set()

        # Python Enums
        for py_enum_file in ["enums.py", "exceptions.py"]:
            py_enums = (
                self.repo_root / "backend_v2" / "models" / py_enum_file
                if py_enum_file == "enums.py"
                else self.repo_root / "backend_v2" / py_enum_file
            )
            if py_enums.exists():
                try:
                    tree = ast.parse(py_enums.read_text(encoding="utf-8"), filename=py_enums.as_posix())
                    for node in ast.walk(tree):
                        match node:
                            case ast.ClassDef(name=enum_name):
                                valid_enums.add(enum_name)
                            case _:
                                pass
                except (OSError, UnicodeDecodeError, SyntaxError) as e:
                    self._add_finding(
                        line_number=0,
                        rule_code="MBD007",
                        category="Enum Hallucination",
                        message=f"Failed to parse {py_enums.as_posix()} for valid enums: {e}",
                        severity=GuardrailSeverity.WARNING,
                        remediation="Ensure enum files in backend_v2 are syntactically valid.",
                    )

        # Flutter Enums (Regex based parsing)
        dart_enums = self.repo_root / "client_app_v2" / "lib" / "core" / "models" / "enums.dart"
        if dart_enums.exists():
            try:
                content = dart_enums.read_text(encoding="utf-8")
                dart_matches = re.findall(r"enum\s+([A-Za-z0-9_]+)", content)
                valid_enums.update(dart_matches)
            except (OSError, UnicodeDecodeError) as e:
                self._add_finding(
                    line_number=0,
                    rule_code="MBD007",
                    category="Enum Hallucination",
                    message=f"Failed to parse {dart_enums.as_posix()} for valid enums: {e}",
                    severity=GuardrailSeverity.WARNING,
                    remediation="Ensure client_app_v2/lib/core/models/enums.dart is readable.",
                )

        pattern = re.compile(r"`([A-Z][a-zA-Z0-9_]+)\.[A-Z0-9_]+`")
        mentioned = set(pattern.findall(self.content))

        for enum_ref in sorted(mentioned):
            if enum_ref not in valid_enums and "DTO" not in enum_ref and "Service" not in enum_ref:
                self._add_finding(
                    line_number=0,
                    rule_code="MBD007",
                    category="Enum Hallucination",
                    message=f"Enum Hallucination: '{enum_ref}' used as an Enum but not found in SSOT enum files.",
                    severity=GuardrailSeverity.WARNING,
                    remediation=f"Ensure '{enum_ref}' is defined in backend_v2/models/enums.py or client_app_v2/lib/core/models/enums.dart.",
                )


def main() -> None:
    """CLI entrypoint for markdown boundaries auditor."""
    parser = argparse.ArgumentParser(description="Audit Markdown files for architectural boundaries.")
    parser.add_argument("--file", type=str, required=True, help="Path to the markdown file to audit.")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print_error(f"File {file_path} does not exist.")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    auditor = MarkdownAuditor(str(file_path), str(repo_root))
    auditor.run_all_checks(exit_on_completion=True)


if __name__ == "__main__":
    main()

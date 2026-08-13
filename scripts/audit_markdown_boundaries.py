"""Audit Markdown Boundaries.

Scans Markdown documents to ensure references, boundaries, and terminology
comply with the architectural standards.
"""

import argparse
import ast
import re
import sys
from pathlib import Path

# ANSI colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_error(msg: str) -> None:
    """Print an error message in red.

    Args:
        msg: The error message.
    """
    print(f"{RED}ERROR: {msg}{RESET}")


def print_success(msg: str) -> None:
    """Print a success message in green.

    Args:
        msg: The success message.
    """
    print(f"{GREEN}SUCCESS: {msg}{RESET}")


class MarkdownAuditor:
    """Auditor for analyzing architectural boundaries in Markdown.

    Attributes:
        file_path: The file to audit.
        repo_root: The root of the repository.
        content: The text content of the file.
        lines: The split lines of the file.
        errors: A list of accumulated audit errors.
    """

    def __init__(self, file_path: str, repo_root: str):
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
        self.errors: list[str] = []

    def run_all_checks(self) -> None:
        """Run all verification checks on the markdown content."""
        self.check_ambiguity()
        self.check_xml_truncation()
        self.check_file_references_and_ast_bounds()
        self.check_class_hallucinations()
        self.check_settings_validation()
        self.check_enum_validation()

        if self.errors:
            print(f"\n{RED}Audit failed with {len(self.errors)} errors:{RESET}")
            for err in self.errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print_success(f"Audit passed for {self.file_path}")
            sys.exit(0)

    def check_ambiguity(self) -> None:
        """Scan for ambiguous terminology that should be avoided."""
        # Scan for ambiguous terms like 'e.g.', 'etc.', 'such as', 'like'
        pattern = re.compile(r"(?:\b|\s)(e\.g\.|etc\.|such as|like)(?:\s|$|[,.])", re.IGNORECASE)
        for i, line in enumerate(self.lines):
            match = pattern.search(line)
            if match:
                self.errors.append(
                    f"Line {i + 1}: Ambiguous language detected '{match.group(1)}'. Use programmatic SSOT references."
                )

    def check_xml_truncation(self) -> None:
        """Verify that specific XML tags are correctly matched and not truncated."""
        # Stack-based XML tag checker for <execution_protocol> and <step>
        tag_pattern = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9_]+)[^>]*>")
        stack = []
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
                        self.errors.append(f"Line {i + 1}: Closing tag </{tag_name}> without opening tag.")
                    else:
                        top_tag, top_line = stack.pop()
                        if top_tag != tag_name:
                            self.errors.append(
                                f"Line {i + 1}: Mismatched closing tag </{tag_name}>. Expected </{top_tag}> from line {top_line}."  # noqa: E501
                            )

        for tag_name, line_num in stack:
            self.errors.append(f"Line {line_num}: Unclosed tag <{tag_name}>.")

    def check_file_references_and_ast_bounds(self) -> None:
        """Check all file references with line boundaries against the AST."""
        # Find @[filepath] or @[filepath#Lxx-Lyy]
        pattern = re.compile(r"@\[([^#\]]+)(?:#L(\d+)-L(\d+))?\]")
        for i, line in enumerate(self.lines):
            for match in pattern.finditer(line):
                rel_path = match.group(1).strip()
                start_line = match.group(2)
                end_line = match.group(3)

                full_path = self.repo_root / rel_path

                # Check for [NEW] or [DELETE] flags
                if "[NEW]" in line or "[DELETE]" in line:
                    continue

                if rel_path.startswith("ki_") and rel_path.endswith(".md"):
                    continue

                if not full_path.exists():
                    self.errors.append(f"Line {i + 1}: Referenced file does not exist: {rel_path}")
                    continue

                if start_line and end_line and full_path.suffix == ".py":
                    self.verify_ast_bounds(full_path, int(start_line), int(end_line), i + 1, rel_path)

    def verify_ast_bounds(
        self, file_path: Path, start_line: int, end_line: int, md_line_num: int, rel_path: str
    ) -> None:
        """Verify that line ranges match a class or function exactly.

        Args:
            file_path: Path to the python file.
            start_line: Start line.
            end_line: End line.
            md_line_num: The markdown line number referencing it.
            rel_path: Relative path string used for error reporting.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)

            valid_bounds = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    node_start = node.lineno
                    if getattr(node, "decorator_list", None):
                        node_start = min(d.lineno for d in node.decorator_list)
                    node_end = getattr(node, "end_lineno", node_start)
                    valid_bounds.append((node_start, node_end))

            if (start_line, end_line) not in valid_bounds:
                self.errors.append(
                    f"Line {md_line_num}: AST Bound mismatch for {rel_path}#L{start_line}-L{end_line}. No exact Class/Function matches these lines."  # noqa: E501
                )

        except SyntaxError:
            self.errors.append(f"Line {md_line_num}: SyntaxError parsing {rel_path} for AST bounding.")
        except Exception as e:
            self.errors.append(f"Line {md_line_num}: Error parsing AST for {rel_path}: {e}")

    def check_class_hallucinations(self) -> None:
        """Scan mentioned DTOs/Classes and ensure they exist in backend_v2."""
        # Extract mentioned DTOs, Caches, Responses, Services (e.g. `UserDTO`)
        pattern = re.compile(r"`([A-Za-z0-9_]+(?:DTO|Cache|Response|Service))`")
        mentioned = set(pattern.findall(self.content))
        if not mentioned:
            return

        # Scan backend_v2 for classes
        valid_classes = set()
        backend_dir = self.repo_root / "backend_v2"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            valid_classes.add(node.name)
                except Exception as e:
                    self.errors.append(f"Failed to parse {py_file} for valid classes: {e}")

        for cls in mentioned:
            if cls not in valid_classes:
                self.errors.append(f"Class Hallucination: '{cls}' mentioned but not found in backend_v2.")

    def check_settings_validation(self) -> None:
        """Validate references to backend settings.py."""
        # Mentioning settings.FOO
        pattern = re.compile(r"\bsettings\.([a-zA-Z0-9_]+)\b")
        mentioned = {m for m in pattern.findall(self.content) if m != "py"}
        if not mentioned:
            return

        settings_path = self.repo_root / "backend_v2" / "settings.py"
        valid_settings = set()
        if settings_path.exists():
            try:
                with open(settings_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == "Settings":
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                valid_settings.add(item.target.id)
                            elif isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        valid_settings.add(target.id)
            except Exception as e:
                self.errors.append(f"Failed to parse {settings_path} for valid settings: {e}")

        for setting in mentioned:
            if setting not in valid_settings:
                self.errors.append(f"Settings Hallucination: 'settings.{setting}' not found in backend_v2/settings.py.")

    def check_enum_validation(self) -> None:
        """Validate references to Enums in backend and flutter models."""
        # Valid enums
        valid_enums = set()

        # Python Enums
        py_enums = self.repo_root / "backend_v2" / "models" / "enums.py"
        if py_enums.exists():
            try:
                with open(py_enums, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        valid_enums.add(node.name)
            except Exception as e:
                self.errors.append(f"Failed to parse {py_enums} for valid enums: {e}")

        # Flutter Enums (Regex based parsing)
        dart_enums = self.repo_root / "client_app_v2" / "lib" / "core" / "models" / "enums.dart"
        if dart_enums.exists():
            try:
                with open(dart_enums, encoding="utf-8") as f:
                    content = f.read()
                dart_matches = re.findall(r"enum\s+([A-Za-z0-9_]+)", content)
                valid_enums.update(dart_matches)
            except Exception as e:
                self.errors.append(f"Failed to parse {dart_enums} for valid enums: {e}")

        # Look for Enum references in markdown like `StatusEnum.VALUE`
        pattern = re.compile(r"`([A-Z][a-zA-Z0-9_]+)\.[A-Z0-9_]+`")
        mentioned = set(pattern.findall(self.content))

        for enum_ref in mentioned:
            if enum_ref not in valid_enums and "DTO" not in enum_ref and "Service" not in enum_ref:
                self.errors.append(
                    f"Enum Hallucination: '{enum_ref}' used as an Enum but not found in SSOT enum files."
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Markdown files for architectural boundaries.")
    parser.add_argument("--file", type=str, required=True, help="Path to the markdown file to audit.")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print_error(f"File {file_path} does not exist.")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent

    auditor = MarkdownAuditor(str(file_path), str(repo_root))
    auditor.run_all_checks()

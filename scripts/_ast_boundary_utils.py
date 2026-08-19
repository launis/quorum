"""AST Boundary and Symbol Verification Utilities.

Shared helper functions for deterministic neuro-symbolic audit gates in Quorum.
"""

import ast
import re
from pathlib import Path


def extract_target_files(content: str) -> list[tuple[str, str, str | None]]:
    """Extract target file references tagged with MODIFY, NEW, or DELETE from Markdown content.

    Returns:
        List of tuples containing (action_tag, clean_file_path, optional_line_bound).
    """
    pattern = re.compile(
        r"\[(MODIFY|NEW|DELETE)\][`\s*:]*@?\[?`?([^\]`\s#]+)(?:#(L\d+-L?\d+))?",
        re.IGNORECASE,
    )
    matches: list[tuple[str, str, str | None]] = []
    for match in pattern.finditer(content):
        action = match.group(1).upper()
        raw_path = match.group(2).strip().strip("`").strip("@").strip("[").strip("]")
        bound = match.group(3)
        if raw_path and not raw_path.startswith("http"):
            normalized_path = Path(raw_path).as_posix()
            bound_str = f"#{bound}" if bound else None
            matches.append((action, normalized_path, bound_str))
    return matches


def parse_line_bound(bound_str: str) -> tuple[int, int] | None:
    """Parse a line bound string like '#L10-L25' or '#L10-25' into (start_line, end_line).

    Returns:
        tuple[int, int] if valid, None otherwise.
    """
    match = re.match(r"#?L?(\d+)-L?(\d+)", bound_str)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    return (start, end) if start <= end else (end, start)


def validate_ast_line_bound(file_path: Path, start_line: int, end_line: int) -> bool:
    """Validate that a .py file contains at least one AST definition node within given line range.

    Checks ClassDef, FunctionDef, and AsyncFunctionDef nodes.
    Returns True if at least one definition node falls within [start_line, end_line], False otherwise.
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return False

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path.as_posix())
    except SyntaxError, UnicodeDecodeError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            node_start = node.lineno
            node_end = getattr(node, "end_lineno", node.lineno)
            if node_start >= start_line and node_end <= end_line:
                return True
            # Also accept if the definition spans across the bounds
            if node_start <= start_line and node_end >= end_line:
                return True
    return False


class SymbolDefinitionVisitor(ast.NodeVisitor):
    """AST visitor to detect definition locations of specific symbol names."""

    def __init__(self, target_symbols: set[str]) -> None:
        self.target_symbols = target_symbols
        self.found_symbols: dict[str, list[int]] = {sym: [] for sym in target_symbols}

    def _record(self, name: str, lineno: int) -> None:
        if name in self.target_symbols:
            self.found_symbols[name].append(lineno)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record(node.name, node.lineno)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record(node.name, node.lineno)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record(node.name, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self._record(node.target.id, node.lineno)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._record(target.id, node.lineno)
        self.generic_visit(node)


def find_symbols_in_python_code(code: str, symbols: set[str]) -> dict[str, list[int]]:
    """Scan Python source code string for definitions of target symbols using AST parsing."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}

    visitor = SymbolDefinitionVisitor(symbols)
    visitor.visit(tree)
    return {sym: lines for sym, lines in visitor.found_symbols.items() if lines}


def extract_deprecated_symbols(content: str) -> set[str]:
    """Extract deprecated symbol names from <demolish> XML blocks and inline markdown phrases."""
    symbols: set[str] = set()
    demolish_blocks = re.findall(r"<demolish>([\s\S]*?)</demolish>", content, re.IGNORECASE)
    for block in demolish_blocks:
        symbols.update(re.findall(r"[`']([a-zA-Z_][a-zA-Z0-9_]*)[`']", block))
        for line in block.strip().splitlines():
            cleaned = line.strip().strip("-*`' ")
            if cleaned and re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", cleaned):
                symbols.add(cleaned)

    inline_matches = re.findall(
        r"(?:deprecated?|eradicate|remove|delete)\s+[`']([a-zA-Z_][a-zA-Z0-9_]*)[`']",
        content,
        re.IGNORECASE,
    )
    symbols.update(inline_matches)
    # Exclude common markdown/language keywords
    reserved_words = {"True", "False", "None", "file", "symbol", "code", "method", "class"}
    return {s for s in symbols if s not in reserved_words and len(s) > 1}

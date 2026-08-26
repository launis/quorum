"""AST Boundary and Symbol Verification Utilities.

Shared helper functions and Pydantic V2 DTOs for deterministic
neuro-symbolic audit gates in Quorum.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class TargetFileReferenceDTO(BaseModel):
    """Pydantic V2 DTO representing an extracted target file from Markdown documentation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    action: str  # MODIFY | NEW | DELETE
    file_path: str
    line_bound: str | None = None


class AstLineBoundDTO(BaseModel):
    """Pydantic V2 DTO representing start and end line bounds."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    start_line: int
    end_line: int


class SymbolDefinitionDTO(BaseModel):
    """Pydantic V2 DTO representing a discovered symbol definition location."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    symbol_name: str
    line_numbers: list[int]


def normalize_target_path(raw_path: str) -> str:
    """Sanitize raw markdown path string into a normalized POSIX relative path.

    Strips @, [, ], backticks, embedded #L line bounds, and whitespace.
    """
    cleaned = raw_path.strip().strip("`").strip("@").strip("[").strip("]")
    cleaned = cleaned.split("#")[0].strip()
    return Path(cleaned).as_posix()


def extract_target_files(content: str) -> list[TargetFileReferenceDTO]:
    """Extract target file references tagged with MODIFY, NEW, or DELETE from Markdown content.

    Returns:
        List of TargetFileReferenceDTO objects.
    """
    pattern = re.compile(
        r"\[(MODIFY|NEW|DELETE)\][`\s*:]*@?\[?`?([^\]`\s#]+)(?:#(L\d+-L?\d+))?",
        re.IGNORECASE,
    )
    matches: list[TargetFileReferenceDTO] = []
    for match in pattern.finditer(content):
        action = match.group(1).upper()
        raw_path = match.group(2)
        bound = match.group(3)
        if raw_path and not raw_path.startswith("http"):
            normalized_path = normalize_target_path(raw_path)
            bound_str = f"#{bound}" if bound else None
            matches.append(
                TargetFileReferenceDTO(
                    action=action,
                    file_path=normalized_path,
                    line_bound=bound_str,
                )
            )
    return matches


def parse_line_bound(bound_str: str) -> AstLineBoundDTO | None:
    """Parse a line bound string like '#L10-L25' or '#L10-25' into AstLineBoundDTO.

    Returns:
        AstLineBoundDTO if valid, None otherwise.
    """
    match = re.match(r"^#?L?(\d+)-L?(\d+)$", bound_str.strip())
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    start_line, end_line = (start, end) if start <= end else (end, start)
    return AstLineBoundDTO(start_line=start_line, end_line=end_line)


def validate_ast_line_bound(file_path: Path, start_line: int, end_line: int) -> bool:
    """Validate that a .py file contains at least one AST definition node within given line range.

    Checks ClassDef, FunctionDef, and AsyncFunctionDef nodes without reflection.
    Returns True if at least one definition node falls within [start_line, end_line], False otherwise.
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return False

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path.as_posix())
    except SyntaxError, UnicodeDecodeError, OSError:
        return False

    for node in ast.walk(tree):
        match node:
            case ast.ClassDef() | ast.FunctionDef() | ast.AsyncFunctionDef():
                node_start = node.lineno
                node_end = node.end_lineno if node.end_lineno is not None else node.lineno
                if node_start >= start_line and node_end <= end_line:
                    return True
                # Also accept if the definition spans across the bounds
                if node_start <= start_line and node_end >= end_line:
                    return True
            case _:
                pass
    return False


class SymbolDefinitionVisitor(ast.NodeVisitor):
    """AST visitor to detect definition locations of specific symbol names with zero reflection."""

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
        match node.target:
            case ast.Name(id=target_id):
                self._record(target_id, node.lineno)
            case _:
                pass
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            match target:
                case ast.Name(id=target_id):
                    self._record(target_id, node.lineno)
                case _:
                    pass
        self.generic_visit(node)


def find_symbols_in_python_code(code: str, symbols: set[str]) -> dict[str, list[int]]:
    """Scan Python source code string for definitions of target symbols using AST parsing with zero reflection."""
    try:
        tree = ast.parse(code)
    except SyntaxError, UnicodeDecodeError:
        return {}

    visitor = SymbolDefinitionVisitor(symbols)
    visitor.visit(tree)
    return {sym: lines for sym, lines in visitor.found_symbols.items() if lines}


def find_symbol_definitions(code: str, symbols: set[str]) -> list[SymbolDefinitionDTO]:
    """Scan Python source code string and return a list of SymbolDefinitionDTO objects."""
    found_map = find_symbols_in_python_code(code, symbols)
    return [SymbolDefinitionDTO(symbol_name=sym, line_numbers=lines) for sym, lines in found_map.items()]


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

"""ISTQB Unit Tests for AST Boundary Utilities (_ast_boundary_utils.py).

Verifies zero-reflection AST parsing, Pydantic V2 DTOs, line bound validations,
symbol extractions, path sanitizations, and fault domain resilience.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Add scripts directory to sys.path
scripts_dir = Path("scripts").resolve()
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from scripts._ast_boundary_utils import (
    AstLineBoundDTO,
    SymbolDefinitionDTO,
    SymbolDefinitionVisitor,
    TargetFileReferenceDTO,
    extract_deprecated_symbols,
    extract_target_files,
    find_symbol_definitions,
    find_symbols_in_python_code,
    normalize_target_path,
    parse_line_bound,
    validate_ast_line_bound,
)


def test_normalize_target_path_partitions() -> None:
    """Test normalize_target_path across all equivalence partitions."""
    # Partition 1: Standard clean path
    assert normalize_target_path("scripts/backend_audit_loop.py") == "scripts/backend_audit_loop.py"

    # Partition 2: At-bracket notation @[...]
    assert normalize_target_path("@[backend_v2/services/execution.py]") == "backend_v2/services/execution.py"

    # Partition 3: Backticks with at-bracket `@[...]`
    assert normalize_target_path("`@[backend_v2/models/v2_core.py]`") == "backend_v2/models/v2_core.py"

    # Partition 4: Embedded line bounds #L10-L25
    assert normalize_target_path("@[backend_v2/models/v2_core.py#L100-L200]") == "backend_v2/models/v2_core.py"

    # Partition 5: Windows backslash normalization to POSIX
    assert normalize_target_path("backend_v2\\services\\orchestrator.py") == "backend_v2/services/orchestrator.py"

    # Partition 6: Whitespace stripping
    assert normalize_target_path("   backend_v2/utils/math.py   ") == "backend_v2/utils/math.py"


def test_extract_target_files_partitions() -> None:
    """Test extract_target_files extracting TargetFileReferenceDTO across diverse formats."""
    markdown_content = """
# Execution Plan Targets

- [MODIFY] `@[backend_v2/services/orchestrator.py#L45-L90]`
- [NEW] @[backend_v2/utils/new_helper.py]
- [DELETE] `@[legacy_utils.py]`
- [modify] backend_v2/settings.py#L1-L10
- Ignore http://example.com/api
- Arbitrary text without action tags
"""
    targets = extract_target_files(markdown_content)
    assert len(targets) == 4

    assert isinstance(targets[0], TargetFileReferenceDTO)
    assert targets[0].action == "MODIFY"
    assert targets[0].file_path == "backend_v2/services/orchestrator.py"
    assert targets[0].line_bound == "#L45-L90"

    assert targets[1].action == "NEW"
    assert targets[1].file_path == "backend_v2/utils/new_helper.py"
    assert targets[1].line_bound is None

    assert targets[2].action == "DELETE"
    assert targets[2].file_path == "legacy_utils.py"
    assert targets[2].line_bound is None

    assert targets[3].action == "MODIFY"
    assert targets[3].file_path == "backend_v2/settings.py"
    assert targets[3].line_bound == "#L1-L10"


def test_parse_line_bound_partitions() -> None:
    """Test parse_line_bound with valid, inverted, and malformed inputs."""
    # Positive Partition 1: Standard format #L10-L25
    b1 = parse_line_bound("#L10-L25")
    assert b1 == AstLineBoundDTO(start_line=10, end_line=25)

    # Positive Partition 2: Non-L second number #L10-25
    b2 = parse_line_bound("#L10-25")
    assert b2 == AstLineBoundDTO(start_line=10, end_line=25)

    # Positive Partition 3: Bare L format L50-L100
    b3 = parse_line_bound("L50-L100")
    assert b3 == AstLineBoundDTO(start_line=50, end_line=100)

    # Positive Partition 4: Inverted bounds #L100-L50
    b4 = parse_line_bound("#L100-L50")
    assert b4 == AstLineBoundDTO(start_line=50, end_line=100)

    # Negative Partition 1: Missing hyphen
    assert parse_line_bound("#L10") is None

    # Negative Partition 2: Non-numeric
    assert parse_line_bound("#Lfoo-Lbar") is None

    # Negative Partition 3: Empty string
    assert parse_line_bound("") is None


def test_validate_ast_line_bound_positive_and_negative(tmp_path: Path) -> None:
    """Test validate_ast_line_bound across ClassDef, FunctionDef, AsyncFunctionDef, and spans."""
    test_py = tmp_path / "sample_service.py"
    test_py.write_text(
        "class MyService:\n"  # Line 1
        "    def run_sync(self) -> None:\n"  # Line 2
        "        pass\n"  # Line 3
        "\n"  # Line 4
        "async def run_async() -> None:\n"  # Line 5
        "    pass\n",  # Line 6
        encoding="utf-8",
    )

    # Positive 1: Bound exactly matches ClassDef (Lines 1-3)
    assert validate_ast_line_bound(test_py, 1, 3) is True

    # Positive 2: Bound encompasses entire file (Lines 1-6)
    assert validate_ast_line_bound(test_py, 1, 6) is True

    # Positive 3: Bound covers AsyncFunctionDef (Lines 5-6)
    assert validate_ast_line_bound(test_py, 5, 6) is True

    # Positive 4: Bound sits strictly inside a definition span (Line 2)
    assert validate_ast_line_bound(test_py, 2, 2) is True

    # Negative 1: Range outside any definition (Line 4)
    assert validate_ast_line_bound(test_py, 4, 4) is False

    # Negative 2: Non-existent file
    assert validate_ast_line_bound(tmp_path / "missing.py", 1, 10) is False

    # Negative 3: Non-Python file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("class FakeClass:\n    pass\n", encoding="utf-8")
    assert validate_ast_line_bound(txt_file, 1, 3) is False

    # Negative 4: Syntax error file (Fault domain resilience)
    bad_py = tmp_path / "broken.py"
    bad_py.write_text("def broken_syntax(:", encoding="utf-8")
    assert validate_ast_line_bound(bad_py, 1, 5) is False

    # Negative 5: Unicode decode error file (Fault domain resilience)
    bad_bytes = tmp_path / "bad_bytes.py"
    bad_bytes.write_bytes(b"\xff\xfe\x00\x00class X: pass")
    assert validate_ast_line_bound(bad_bytes, 1, 5) is False


def test_find_symbols_and_definitions() -> None:
    """Test AST symbol extraction and SymbolDefinitionDTO creation."""
    code = """
class UserService:
    pass

def authenticate_user() -> bool:
    return True

async def sync_remote_data() -> None:
    pass

MAX_CONNECTIONS: int = 100
DEFAULT_TIMEOUT = 30
ignored_var = 1
"""
    target_symbols = {
        "UserService",
        "authenticate_user",
        "sync_remote_data",
        "MAX_CONNECTIONS",
        "DEFAULT_TIMEOUT",
        "NonExistentSymbol",
    }

    found_dict = find_symbols_in_python_code(code, target_symbols)
    assert "UserService" in found_dict
    assert "authenticate_user" in found_dict
    assert "sync_remote_data" in found_dict
    assert "MAX_CONNECTIONS" in found_dict
    assert "DEFAULT_TIMEOUT" in found_dict
    assert "NonExistentSymbol" not in found_dict

    dtos = find_symbol_definitions(code, target_symbols)
    assert len(dtos) == 5
    dto_names = {d.symbol_name for d in dtos}
    assert dto_names == {
        "UserService",
        "authenticate_user",
        "sync_remote_data",
        "MAX_CONNECTIONS",
        "DEFAULT_TIMEOUT",
    }
    for d in dtos:
        assert isinstance(d, SymbolDefinitionDTO)
        assert len(d.line_numbers) > 0


def test_extract_deprecated_symbols_partitions() -> None:
    """Test extract_deprecated_symbols on <demolish> tags and inline natural language."""
    content = """
# Deprecation Plan
<demolish>
  `legacy_parser`
  - old_auth_handler
  `outdated_dto`
</demolish>

We also need to deprecate `old_pipeline_v1` and eradicate `v1_runner`.
Please remove `dead_code_fn` immediately.
Words like file, class, method, True, False, None should be excluded.
"""
    symbols = extract_deprecated_symbols(content)
    assert "legacy_parser" in symbols
    assert "old_auth_handler" in symbols
    assert "outdated_dto" in symbols
    assert "old_pipeline_v1" in symbols
    assert "v1_runner" in symbols
    assert "dead_code_fn" in symbols
    assert "file" not in symbols
    assert "class" not in symbols
    assert "True" not in symbols


def test_symbol_definition_visitor_direct() -> None:
    """Test SymbolDefinitionVisitor direct callbacks."""
    visitor = SymbolDefinitionVisitor({"TargetClass", "target_func", "var_a", "var_b"})
    sample_code = """
class TargetClass:
    pass

def target_func():
    pass

async def target_async():
    pass

var_a: int = 1
var_b = 2
"""
    tree = ast.parse(sample_code)
    visitor.visit(tree)
    assert len(visitor.found_symbols["TargetClass"]) == 1
    assert len(visitor.found_symbols["target_func"]) == 1
    assert len(visitor.found_symbols["var_a"]) == 1
    assert len(visitor.found_symbols["var_b"]) == 1


def test_zero_reflection_in_ast_boundary_utils() -> None:
    """Zero-Reflection Compliance Test: Verify 0 getattr or hasattr calls in _ast_boundary_utils.py."""
    source_file = Path("scripts/_ast_boundary_utils.py").resolve()
    assert source_file.exists()

    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    reflection_calls: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        match node:
            case ast.Call(func=ast.Name(id=func_name)) if func_name in ("getattr", "hasattr"):
                reflection_calls.append((func_name, node.lineno))
            case _:
                pass

    assert reflection_calls == [], f"Forbidden reflection calls found in _ast_boundary_utils.py: {reflection_calls}"

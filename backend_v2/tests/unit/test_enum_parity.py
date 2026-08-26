import ast
import os
import re

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DART_ENUM_PATH = os.path.join(REPO_ROOT, "client_app_v2", "lib", "core", "models", "enums.dart")
PYTHON_ENUMS_PATH = os.path.join(REPO_ROOT, "backend_v2", "models", "enums.py")
PYTHON_V2_CORE_PATH = os.path.join(REPO_ROOT, "backend_v2", "models", "v2_core.py")
PYTHON_SDUI_PATH = os.path.join(REPO_ROOT, "backend_v2", "models", "view", "sdui.py")
JINJA_TEMPLATE_PATH = os.path.join(REPO_ROOT, "backend_v2", "templates", "report_template.jinja2")


def read_file(path: str) -> str:
    """Read a text file with UTF-8 encoding."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_dart_enum_json_values(dart_code: str, enum_name: str) -> set[str]:
    """Extract all @JsonValue('...') strings for a specific Dart enum."""
    enum_pattern = rf"enum\s+{enum_name}\s*\{{(.*?)\}}"
    match = re.search(enum_pattern, dart_code, re.DOTALL)
    if not match:
        raise ValueError(f"Enum {enum_name} not found in Dart file.")

    enum_body = match.group(1)
    values = re.findall(r"@JsonValue\(['\"]([^'\"]+)['\"]\)", enum_body)
    return set(values)


def extract_python_enum_values_ast(python_code: str, enum_name: str) -> set[str]:
    """Extract member string values of a Python StrEnum or Enum class via AST parsing."""
    tree = ast.parse(python_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == enum_name:
            values: set[str] = set()
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        values.add(stmt.value.value)
                elif isinstance(stmt, ast.AnnAssign):
                    if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        values.add(stmt.value.value)
            return values
    raise ValueError(f"Enum {enum_name} not found in Python AST.")


def extract_python_literal_values_ast(python_code: str, class_name: str, field_name: str) -> set[str]:
    """Extract string values from a Literal[...] type hint in a Pydantic model via AST."""
    tree = ast.parse(python_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    target_id = stmt.target.id if isinstance(stmt.target, ast.Name) else None
                    if target_id == field_name and stmt.annotation:
                        # Find Literal slice
                        for child in ast.walk(stmt.annotation):
                            if isinstance(child, ast.Subscript):
                                if isinstance(child.value, ast.Name) and child.value.id == "Literal":
                                    values: set[str] = set()
                                    if isinstance(child.slice, ast.Tuple):
                                        for elt in child.slice.elts:
                                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                                values.add(elt.value)
                                    elif isinstance(child.slice, ast.Constant) and isinstance(child.slice.value, str):
                                        values.add(child.slice.value)
                                    return values
    raise ValueError(f"Field {field_name} with Literal not found in {class_name}.")


def assert_enum_parity(dart_code: str, python_code: str, enum_name: str) -> None:
    """Assert parity between a Dart enum and a Python StrEnum."""
    dart_values = extract_dart_enum_json_values(dart_code, enum_name)
    py_values = extract_python_enum_values_ast(python_code, enum_name)

    missing_in_dart = py_values - dart_values
    missing_in_python = dart_values - py_values

    assert not missing_in_dart, f"Missing in Dart {enum_name}: {missing_in_dart}"
    assert not missing_in_python, f"Missing in Python {enum_name}: {missing_in_python}"


def test_scoring_strategy_parity() -> None:
    """Verify ScoringStrategy members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "ScoringStrategy")


def test_xai_extension_type_parity() -> None:
    """Verify XaiExtensionType members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "XaiExtensionType")


def test_visual_intent_parity() -> None:
    """Verify VisualIntent members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "VisualIntent")


def test_execution_status_parity() -> None:
    """Verify ExecutionStatus members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "ExecutionStatus")


def test_historical_context_mode_parity() -> None:
    """Verify HistoricalContextMode members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "HistoricalContextMode")


def test_display_scale_parity() -> None:
    """Verify DisplayScale members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "DisplayScale")


def test_target_block_type_parity() -> None:
    """Verify TargetBlockType members match between Python and Dart."""
    assert_enum_parity(read_file(DART_ENUM_PATH), read_file(PYTHON_ENUMS_PATH), "TargetBlockType")


def test_extract_dart_enum_json_values_not_found() -> None:
    """Negative test: Missing enum in Dart raises ValueError."""
    with pytest.raises(ValueError, match="Enum NonExistentEnum not found"):
        extract_dart_enum_json_values("enum Other { @JsonValue('x') x }", "NonExistentEnum")


def test_extract_python_enum_values_ast_not_found() -> None:
    """Negative test: Missing enum in Python AST raises ValueError."""
    with pytest.raises(ValueError, match="Enum NonExistentEnum not found"):
        extract_python_enum_values_ast("class Other(StrEnum): X = 'x'", "NonExistentEnum")


def test_extract_python_literal_values_ast_not_found() -> None:
    """Negative test: Missing class or Literal field in Python AST raises ValueError."""
    with pytest.raises(ValueError, match="Field non_existent with Literal not found"):
        extract_python_literal_values_ast("class MyModel: other: str = 'x'", "MyModel", "non_existent")


def test_extract_python_literal_values_ast_single_constant() -> None:
    """Positive test: Single Literal value extraction."""
    code = "class MyModel: single: Literal['only_one'] = 'only_one'"
    res = extract_python_literal_values_ast(code, "MyModel", "single")
    assert res == {"only_one"}


def test_enum_l10n_keys() -> None:
    """Verify that all members of UI-facing enums resolve to a valid non-empty l10n_key."""
    from backend_v2.models.enums import DisplayScale, ScoringStrategy, XaiExtensionType

    for scale_member in DisplayScale:
        assert scale_member.l10n_key, f"Missing l10n_key for DisplayScale.{scale_member.name}"
        assert isinstance(scale_member.l10n_key, str)
        assert scale_member.l10n_key.startswith("displayScale")

    for strategy_member in ScoringStrategy:
        assert strategy_member.l10n_key, f"Missing l10n_key for ScoringStrategy.{strategy_member.name}"
        assert isinstance(strategy_member.l10n_key, str)
        assert strategy_member.l10n_key.startswith("strategy")

    # XAI extensions that are exposed in UI
    for xai_member in [
        XaiExtensionType.COACHING,
        XaiExtensionType.JUSTIFICATION,
        XaiExtensionType.FALSIFICATION,
        XaiExtensionType.MISSING_CONTEXT,
        XaiExtensionType.THEORY_LINK,
        XaiExtensionType.RISK_FLAG,
        XaiExtensionType.REMEDIATION_STEPS,
        XaiExtensionType.EMOTIONAL_SENTIMENT,
        XaiExtensionType.VARIANCE_VALIDATION,
        XaiExtensionType.AUTHENTICITY_EVALUATION,
    ]:
        assert xai_member.l10n_key, f"Missing l10n_key for XaiExtensionType.{xai_member.name}"
        assert isinstance(xai_member.l10n_key, str)

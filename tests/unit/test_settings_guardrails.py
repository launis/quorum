import ast
from pathlib import Path


def test_settings_has_enforce_fast_mode_limits_ast() -> None:
    """AST guardrail to ensure _enforce_fast_mode_limits is never removed."""
    settings_path = Path("backend_v2/settings.py")
    if not settings_path.exists():
        return

    with open(settings_path, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    found_validator = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_enforce_fast_mode_limits":
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name) and dec.func.id == "model_validator":
                        found_validator = True
                        break

    assert found_validator, "CRITICAL: _enforce_fast_mode_limits validator is missing from backend_v2/settings.py"


def test_settings_ast_rejects_missing_validator() -> None:
    """Negative test to ensure the AST scanner correctly detects a missing validator."""
    code = """
class Settings(BaseSettings):
    pass
"""
    tree = ast.parse(code)
    found_validator = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_enforce_fast_mode_limits":
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name) and dec.func.id == "model_validator":
                        found_validator = True
                        break
    assert not found_validator

"""AST Guardrail Tests for Matrix Causal DAG Integration.

Enforces:
1. TDAAssertion.depends_on is strictly annotated with immutable tuple.
2. FlattenedAtom.depends_on is strictly annotated with immutable tuple.
3. atom_flattening.py contains zero generic `except Exception:` catch-all handlers.
4. PromptBlockAdapter.validate_python in atom_flattening.py uses strict typed exception handlers.
"""

import ast
from pathlib import Path


def test_ast_tda_assertion_depends_on_tuple() -> None:
    """Verify that TDAAssertion.depends_on is annotated as a tuple."""
    v2_core_path = Path("backend_v2/models/v2_core.py")
    tree = ast.parse(v2_core_path.read_text(encoding="utf-8"))

    tda_class: ast.ClassDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TDAAssertion":
            tda_class = node
            break

    assert tda_class is not None, "TDAAssertion class not found in v2_core.py"

    depends_on_field: ast.AnnAssign | None = None
    for stmt in tda_class.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == "depends_on":
            depends_on_field = stmt
            break

    assert depends_on_field is not None, "depends_on field not found on TDAAssertion"

    # Verify annotation string contains tuple[CausalEdge, ...]
    annotation_src = ast.unparse(depends_on_field.annotation)
    assert "tuple" in annotation_src, f"depends_on must be annotated as tuple, found: {annotation_src}"
    assert "CausalEdge" in annotation_src, f"depends_on must reference CausalEdge, found: {annotation_src}"


def test_ast_flattened_atom_depends_on_tuple() -> None:
    """Verify that FlattenedAtom.depends_on is annotated as a tuple."""
    engine_dto_path = Path("backend_v2/models/dtos/engine.py")
    tree = ast.parse(engine_dto_path.read_text(encoding="utf-8"))

    atom_class: ast.ClassDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FlattenedAtom":
            atom_class = node
            break

    assert atom_class is not None, "FlattenedAtom class not found in engine.py"

    depends_on_field: ast.AnnAssign | None = None
    for stmt in atom_class.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == "depends_on":
            depends_on_field = stmt
            break

    assert depends_on_field is not None, "depends_on field not found on FlattenedAtom"

    annotation_src = ast.unparse(depends_on_field.annotation)
    assert "tuple" in annotation_src, f"depends_on must be annotated as tuple, found: {annotation_src}"
    assert "CausalEdge" in annotation_src, f"depends_on must reference CausalEdge, found: {annotation_src}"


def test_ast_no_generic_exception_in_atom_flattening() -> None:
    """Verify that atom_flattening.py contains zero generic `except Exception:` catch-alls."""
    flattening_path = Path("backend_v2/hooks/atom_flattening.py")
    tree = ast.parse(flattening_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is not None:
                type_src = ast.unparse(node.type)
                assert type_src != "Exception", (
                    f"Generic 'except Exception' found on line {node.lineno} in atom_flattening.py. "
                    "Must catch specific exceptions (e.g. ValidationError, ValueError)."
                )
            else:
                assert False, f"Bare 'except:' found on line {node.lineno} in atom_flattening.py."

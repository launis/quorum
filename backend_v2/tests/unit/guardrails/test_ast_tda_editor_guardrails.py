"""AST Guardrail Tests for TDA Assertion ContrastivePairDTO Migration and Input Modernization.

Enforces:
1. TDAAssertion.contrastive_example is strictly annotated as ContrastivePairDTO | None.
2. FlattenedAtom defines typed contrastive_example, acceptance_criteria, anti_patterns, and syntactic_anchors.
3. atom_flattening.py contains zero anonymous tuple state containers.
"""

from __future__ import annotations

import ast
from pathlib import Path


def test_ast_tda_assertion_contrastive_example() -> None:
    """Verify that TDAAssertion.contrastive_example is strictly annotated as ContrastivePairDTO | None."""
    v2_core_path = Path("backend_v2/models/v2_core.py")
    tree = ast.parse(v2_core_path.read_text(encoding="utf-8"))

    tda_class: ast.ClassDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TDAAssertion":
            tda_class = node
            break

    assert tda_class is not None, "TDAAssertion class not found in v2_core.py"

    contrastive_field: ast.AnnAssign | None = None
    for stmt in tda_class.body:
        if (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == "contrastive_example"
        ):
            contrastive_field = stmt
            break

    assert contrastive_field is not None, "contrastive_example field not found on TDAAssertion"

    annotation_src = ast.unparse(contrastive_field.annotation)
    assert "ContrastivePairDTO" in annotation_src, (
        f"contrastive_example must reference ContrastivePairDTO, found: {annotation_src}"
    )
    assert "None" in annotation_src, (
        f"contrastive_example must allow None, found: {annotation_src}"
    )
    # Ensure raw 'str' is NOT permitted in the type annotation
    assert "str" not in annotation_src.replace("ContrastivePairDTO", ""), (
        f"contrastive_example must not allow loose str, found: {annotation_src}"
    )


def test_ast_flattened_atom_structured_fields() -> None:
    """Verify that FlattenedAtom defines structured fields instead of loose strings."""
    engine_path = Path("backend_v2/models/dtos/engine.py")
    tree = ast.parse(engine_path.read_text(encoding="utf-8"))

    atom_class: ast.ClassDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FlattenedAtom":
            atom_class = node
            break

    assert atom_class is not None, "FlattenedAtom class not found in engine.py"

    fields: dict[str, str] = {}
    for stmt in atom_class.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            fields[stmt.target.id] = ast.unparse(stmt.annotation)

    assert "contrastive_example" in fields, "FlattenedAtom lacks contrastive_example"
    assert "ContrastivePairDTO" in fields["contrastive_example"]

    assert "acceptance_criteria" in fields, "FlattenedAtom lacks acceptance_criteria"
    assert "AcceptanceCriterion" in fields["acceptance_criteria"]

    assert "anti_patterns" in fields, "FlattenedAtom lacks anti_patterns"
    assert "AntiPattern" in fields["anti_patterns"]

    assert "syntactic_anchors" in fields, "FlattenedAtom lacks syntactic_anchors"
    assert "tuple" in fields["syntactic_anchors"]


def test_ast_atom_flattening_no_anonymous_tuple_hell() -> None:
    """Verify atom_flattening.py does not contain anonymous tuple containers or positional indexing."""
    flattening_path = Path("backend_v2/hooks/atom_flattening.py")
    content = flattening_path.read_text(encoding="utf-8")

    # Ban anonymous 6-tuple indexing anti-patterns
    assert "current_atom[5]" not in content, "Found positional indexing [5] in atom_flattening.py"
    assert "current_atom[0]" not in content, "Found positional indexing [0] in atom_flattening.py"
    assert "val[0]" not in content, "Found positional indexing val[0] in atom_flattening.py"

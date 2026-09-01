"""AST Guardrail Test Suite for Prompt Block Field Migration and Zero Fallbacks."""

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# AST Scanning Helper Utilities
# ---------------------------------------------------------------------------


def scan_class_for_field(tree: ast.AST, class_name: str, field_name: str) -> bool:
    """Scan AST tree for a class definition and check if field_name is defined.

    Args:
        tree: Parsed AST tree.
        class_name: Name of the class to inspect.
        field_name: Target attribute/field name.

    Returns:
        True if the field is defined in the class body, False otherwise.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                    and item.target.id == field_name
                ):
                    return True
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == field_name:
                            return True
    return False


def scan_for_match_case_ai_description_guards(tree: ast.AST) -> list[int]:
    """Scan AST tree for any match-case guards testing .ai_description.

    Args:
        tree: Parsed AST tree.

    Returns:
        List of line numbers where match-case guards check ai_description.
    """
    violations: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.match_case) and node.guard is not None:
            for child in ast.walk(node.guard):
                if isinstance(child, ast.Attribute) and child.attr == "ai_description":
                    violations.append(node.guard.lineno)
    return violations


def scan_for_or_ai_description_chains(tree: ast.AST) -> list[int]:
    """Scan AST tree for Boolean 'or' operations accessing .ai_description.

    Args:
        tree: Parsed AST tree.

    Returns:
        List of line numbers with boolean 'or' chains containing ai_description.
    """
    violations: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            for value in node.values:
                for child in ast.walk(value):
                    if isinstance(child, ast.Attribute) and child.attr == "ai_description":
                        violations.append(node.lineno)
    return violations


def scan_for_evidence_literal_fallback(tree: ast.AST) -> list[int]:
    """Scan AST tree for 'or "Evidence"' literal fallbacks.

    Args:
        tree: Parsed AST tree.

    Returns:
        List of line numbers with 'or "Evidence"' patterns.
    """
    violations: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            for val in node.values:
                if isinstance(val, ast.Constant) and val.value == "Evidence":
                    violations.append(node.lineno)
        if isinstance(node, ast.IfExp):
            if isinstance(node.orelse, ast.Constant) and node.orelse.value == "Evidence":
                violations.append(node.lineno)
    return violations


# ---------------------------------------------------------------------------
# Test Contracts
# ---------------------------------------------------------------------------


def test_ast_prompt_block_base_has_no_ai_description() -> None:
    """Verify PromptBlockBase in prompt_blocks.py AST does NOT define ai_description."""
    file_path = Path("backend_v2/models/domain/prompt_blocks.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    assert not scan_class_for_field(tree, "PromptBlockBase", "ai_description"), (
        "PromptBlockBase must NOT define ai_description"
    )


def test_ast_matrix_prompt_block_has_ai_description() -> None:
    """Verify MatrixPromptBlock in prompt_blocks.py AST defines ai_description."""
    file_path = Path("backend_v2/models/domain/prompt_blocks.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    assert scan_class_for_field(tree, "MatrixPromptBlock", "ai_description"), (
        "MatrixPromptBlock must explicitly define ai_description"
    )


def test_ast_non_matrix_prompt_blocks_have_no_ai_description() -> None:
    """Verify non-matrix prompt block classes do NOT define ai_description."""
    file_path = Path("backend_v2/models/domain/prompt_blocks.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    non_matrix_classes = [
        "PersonaPromptBlock",
        "SystemRulePromptBlock",
        "ProtocolPromptBlock",
        "TaskDefinitionPromptBlock",
        "RuntimeVariablesPromptBlock",
    ]
    for cls_name in non_matrix_classes:
        assert not scan_class_for_field(tree, cls_name, "ai_description"), f"{cls_name} must NOT define ai_description"


def test_ast_prompt_factory_has_no_ai_description_case_guards() -> None:
    """Verify prompt_factory.py AST contains 0 case guards testing ai_description."""
    file_path = Path("backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    violations = scan_for_match_case_ai_description_guards(tree)
    assert len(violations) == 0, f"Found case _ if *.ai_description guards in prompt_factory.py at lines: {violations}"


def test_ast_localization_compiler_has_no_ai_description_case_guards() -> None:
    """Verify localization_compiler.py AST contains 0 case guards testing ai_description."""
    file_path = Path("backend_v2/services/orchestrator/localization_compiler.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    violations = scan_for_match_case_ai_description_guards(tree)
    assert len(violations) == 0, (
        f"Found case _ if *.ai_description guards in localization_compiler.py at lines: {violations}"
    )


def test_ast_simulation_service_has_no_or_ai_description() -> None:
    """Verify simulation_service.py AST contains 0 'or data.ai_description' chains."""
    file_path = Path("backend_v2/services/studio/simulation_service.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    violations = scan_for_or_ai_description_chains(tree)
    assert len(violations) == 0, (
        f"Found 'or *.ai_description' fallback chains in simulation_service.py at lines: {violations}"
    )


def test_ast_matrix_explanation_service_has_no_evidence_fallback() -> None:
    r"""Verify matrix_explanation_service.py AST contains 0 'or \"Evidence\"' fallbacks."""
    file_path = Path("backend_v2/services/orchestrator/matrix_explanation_service.py")
    assert file_path.exists(), f"{file_path} must exist"
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    violations = scan_for_evidence_literal_fallback(tree)
    assert len(violations) == 0, (
        f"Found 'or \"Evidence\"' literal fallbacks in matrix_explanation_service.py at lines: {violations}"
    )


# ---------------------------------------------------------------------------
# Negative AST Scanner Tests
# ---------------------------------------------------------------------------


def test_ast_guardrail_catches_invalid_case_guard_negative() -> None:
    """Negative test: Prove scanner catches match-case guard with ai_description."""
    code = """
match block:
    case PersonaPromptBlock() if block.ai_description:
        return block.ai_description
"""
    tree = ast.parse(code)
    violations = scan_for_match_case_ai_description_guards(tree)
    assert len(violations) == 1, "Scanner must detect case guard checking ai_description"


def test_ast_guardrail_catches_invalid_or_chain_negative() -> None:
    """Negative test: Prove scanner catches 'or data.ai_description' chain."""
    code = """
rendered = data.role_enforcement or data.ai_description or ""
"""
    tree = ast.parse(code)
    violations = scan_for_or_ai_description_chains(tree)
    assert len(violations) == 1, "Scanner must detect 'or data.ai_description' fallback chain"


def test_ast_guardrail_catches_invalid_evidence_literal_negative() -> None:
    r"""Negative test: Prove scanner catches 'or \"Evidence\"' fallback."""
    code = """
claim_name = tda_to_claim.get(tda_id, "Evidence") or "Evidence"
"""
    tree = ast.parse(code)
    violations = scan_for_evidence_literal_fallback(tree)
    assert len(violations) == 1, "Scanner must detect 'or \"Evidence\"' literal fallback"

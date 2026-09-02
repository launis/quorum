"""AST and Seed Guardrail Test Suite for MatrixClaim and TDAAssertion."""

import ast
import json
from pathlib import Path

from backend_v2.settings import get_settings

# ---------------------------------------------------------------------------
# AST Scanning Helper Utilities (per ki_ast_guardrail_testing.md)
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


def scan_class_field_annotation_has_min_length_10(tree: ast.AST, class_name: str, field_name: str) -> bool:
    """Scan AST for field annotation enforcing StringConstraints(min_length=10).

    Args:
        tree: Parsed AST tree.
        class_name: Target class name.
        field_name: Target field name.

    Returns:
        True if annotation or Field contains min_length >= 10.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                    and item.target.id == field_name
                ):
                    for child in ast.walk(item):
                        if isinstance(child, ast.keyword) and child.arg == "min_length":
                            if (
                                isinstance(child.value, ast.Constant)
                                and isinstance(child.value.value, int)
                                and child.value.value >= 10
                            ):
                                return True
                        if (
                            isinstance(child, ast.Call)
                            and isinstance(child.func, ast.Name)
                            and child.func.id == "StringConstraints"
                        ):
                            for kw in child.keywords:
                                if (
                                    kw.arg == "min_length"
                                    and isinstance(kw.value, ast.Constant)
                                    and isinstance(kw.value.value, int)
                                    and kw.value.value >= 10
                                ):
                                    return True
    return False


def scan_file_for_hasattr_getattr(tree: ast.AST) -> list[tuple[int, str]]:
    """Scan AST tree for any invocations of getattr() or hasattr().

    Args:
        tree: Parsed AST tree.

    Returns:
        List of (lineno, function_name) tuples where getattr or hasattr is called.
    """
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr"):
                violations.append((node.lineno, node.func.id))
    return violations


def scan_file_for_claim_ai_description_access(tree: ast.AST) -> list[int]:
    """Scan AST tree for any claim.ai_description or getattr(claim, 'ai_description') access.

    Args:
        tree: Parsed AST tree.

    Returns:
        List of line numbers with violations.
    """
    violations: list[int] = []
    for node in ast.walk(tree):
        # Check claim.ai_description
        if isinstance(node, ast.Attribute) and node.attr == "ai_description":
            if isinstance(node.value, ast.Name) and "claim" in node.value.id:
                violations.append(node.lineno)
        # Check getattr(claim, "ai_description", ...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 2:
                first_arg = node.args[0]
                second_arg = node.args[1]
                if isinstance(first_arg, ast.Name) and "claim" in first_arg.id:
                    if isinstance(second_arg, ast.Constant) and second_arg.value == "ai_description":
                        violations.append(node.lineno)
    return violations


# ---------------------------------------------------------------------------
# Test Contracts (1-9)
# ---------------------------------------------------------------------------


def test_seed_claims_have_no_ai_description() -> None:
    """Verify seed_data.json has 0 matrix claims containing ai_description."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    assert seed_path.exists(), "seed_data.json must exist"
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    violations = []
    for block in prompt_blocks:
        if block.get("category_id") == "matrix":
            for scale in block.get("scales", []):
                for claim in scale.get("claims", []):
                    if "ai_description" in claim:
                        violations.append((block.get("id"), scale.get("score"), claim.get("label")))

    assert len(violations) == 0, f"Found {len(violations)} matrix claims with ai_description: {violations}"


def test_seed_claims_all_tda_assertions_have_valid_concept_description() -> None:
    """Verify all tda_assertions in seed_data.json have concept_description with len >= 10."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    assert seed_path.exists(), "seed_data.json must exist"
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    short_assertions = []
    total_assertions = 0
    for block in prompt_blocks:
        if block.get("category_id") == "matrix":
            for scale in block.get("scales", []):
                for claim in scale.get("claims", []):
                    for assertion in claim.get("tda_assertions", []):
                        total_assertions += 1
                        desc = assertion.get("concept_description", "")
                        if not isinstance(desc, str) or len(desc.strip()) < 10:
                            short_assertions.append((assertion.get("tda_id"), desc))

    assert total_assertions >= 152, f"Expected at least 152 assertions in seed, found {total_assertions}"
    assert len(short_assertions) == 0, (
        f"Found {len(short_assertions)} assertions with concept_description < 10 chars: {short_assertions}"
    )


def test_settings_tda_concept_min_length_defined() -> None:
    """Verify Settings defines tda_concept_min_length == 10."""
    settings = get_settings()
    assert hasattr(settings, "tda_concept_min_length"), "settings.tda_concept_min_length must be defined"
    assert settings.tda_concept_min_length == 10, "settings.tda_concept_min_length must equal 10"


def test_ast_matrix_claim_has_no_ai_description_field() -> None:
    """Verify MatrixClaim class in v2_core.py AST does not define ai_description."""
    model_path = Path("backend_v2/models/v2_core.py")
    assert model_path.exists(), "v2_core.py must exist"
    with open(model_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(model_path))

    has_ai_desc = scan_class_for_field(tree, "MatrixClaim", "ai_description")
    assert not has_ai_desc, "MatrixClaim in v2_core.py must NOT define ai_description"


def test_ast_tda_assertion_has_string_constraints_min_length_10() -> None:
    """Verify TDAAssertion.concept_description enforces min_length=10 via AST."""
    model_path = Path("backend_v2/models/v2_core.py")
    assert model_path.exists(), "v2_core.py must exist"
    with open(model_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(model_path))

    has_min_len = scan_class_field_annotation_has_min_length_10(tree, "TDAAssertion", "concept_description")
    assert has_min_len, "TDAAssertion.concept_description must enforce StringConstraints min_length >= 10"


def test_simulation_service_ast_no_claim_ai_description_access() -> None:
    """Verify simulation_service.py AST contains 0 claim.ai_description accesses."""
    service_path = Path("backend_v2/services/studio/simulation_service.py")
    assert service_path.exists(), "simulation_service.py must exist"
    with open(service_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(service_path))

    violations = scan_file_for_claim_ai_description_access(tree)
    assert len(violations) == 0, f"Found claim.ai_description accesses on lines: {violations}"


def test_simulation_service_ast_no_hasattr_getattr() -> None:
    """Verify simulation_service.py AST contains 0 getattr and 0 hasattr calls."""
    service_path = Path("backend_v2/services/studio/simulation_service.py")
    assert service_path.exists(), "simulation_service.py must exist"
    with open(service_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(service_path))

    violations = scan_file_for_hasattr_getattr(tree)
    assert len(violations) == 0, f"Found getattr/hasattr calls: {violations}"


def test_ast_guardrail_catches_invalid_matrix_claim_negative() -> None:
    """Negative test: Prove AST scanner detects invalid MatrixClaim containing ai_description."""
    invalid_code = """
class MatrixClaim(BaseModel):
    label: I18nText
    ai_description: str = Field(description="Legacy field")
    tda_assertions: list[TDAAssertion]
"""
    mock_tree = ast.parse(invalid_code)
    has_field = scan_class_for_field(mock_tree, "MatrixClaim", "ai_description")
    assert has_field is True, "AST scanner must detect ai_description field in mock MatrixClaim"


def test_ast_guardrail_catches_missing_string_constraints_negative() -> None:
    """Negative test: Prove AST scanner detects TDAAssertion without min_length >= 10 constraint."""
    invalid_code = """
class TDAAssertion(BaseModel):
    concept_description: str = Field(description="Unconstrained string")
"""
    mock_tree = ast.parse(invalid_code)
    has_min_len = scan_class_field_annotation_has_min_length_10(mock_tree, "TDAAssertion", "concept_description")
    assert has_min_len is False, "AST scanner must detect missing min_length constraint in mock TDAAssertion"

    valid_code = """
class TDAAssertion(BaseModel):
    concept_description: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)]
"""
    mock_valid_tree = ast.parse(valid_code)
    has_min_len_valid = scan_class_field_annotation_has_min_length_10(
        mock_valid_tree, "TDAAssertion", "concept_description"
    )
    assert has_min_len_valid is True, "AST scanner must recognize StringConstraints min_length >= 10"

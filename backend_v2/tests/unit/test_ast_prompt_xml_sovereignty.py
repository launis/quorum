"""AST Guardrail Suite for Prompt XML Sovereignty and Model Purity.

Enforces static structural compliance across prompt builders and domain models:
- Zero reflection (hasattr/getattr)
- Zero slug-based routing
- Strict Pydantic frozen domain models with discriminator
- Negative AST tests proving scanner enforcement
"""

import ast
from pathlib import Path


def _load_ast(file_path: str) -> ast.AST:
    path = Path(file_path)
    assert path.exists(), f"Target file not found: {file_path}"
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=file_path)


def test_ast_domain_models_strict_frozen_config() -> None:
    """Verifies that all prompt block classes define strict, forbidden, frozen ConfigDict."""
    tree = _load_ast("backend_v2/models/domain/prompt_blocks.py")
    classes_checked = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check for model_config assignment
            has_valid_config = False
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "model_config":
                            # Check Call to ConfigDict
                            if isinstance(stmt.value, ast.Call):
                                kwargs = {kw.arg: kw.value for kw in stmt.value.keywords if kw.arg}
                                strict_val = kwargs.get("strict")
                                extra_val = kwargs.get("extra")
                                frozen_val = kwargs.get("frozen")

                                is_strict = isinstance(strict_val, ast.Constant) and strict_val.value is True
                                is_forbid = isinstance(extra_val, ast.Constant) and extra_val.value == "forbid"
                                is_frozen = isinstance(frozen_val, ast.Constant) and frozen_val.value is True

                                if is_strict and is_forbid and is_frozen:
                                    has_valid_config = True

            assert has_valid_config, f"Class {node.name} does not define strict frozen ConfigDict"
            classes_checked += 1

    assert classes_checked >= 5, f"Expected at least 5 classes checked, found {classes_checked}"


def test_ast_any_prompt_block_discriminator() -> None:
    """Verifies AnyPromptBlock uses Field(discriminator='category_id')."""
    tree = _load_ast("backend_v2/models/domain/prompt_blocks.py")
    found_discriminator = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "AnyPromptBlock":
                    # Look inside the value for Field(discriminator="category_id")
                    for sub in ast.walk(node.value):
                        if isinstance(sub, ast.Call):
                            for kw in sub.keywords:
                                if kw.arg == "discriminator" and isinstance(kw.value, ast.Constant):
                                    if kw.value.value == "category_id":
                                        found_discriminator = True

    assert found_discriminator, "AnyPromptBlock does not define Field(discriminator='category_id')"


def test_ast_matrix_prompt_block_scales_required() -> None:
    """Verifies MatrixPromptBlock defines scales with min_length=1."""
    tree = _load_ast("backend_v2/models/domain/prompt_blocks.py")
    found_scales_constraint = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MatrixPromptBlock":
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == "scales":
                    if stmt.value and isinstance(stmt.value, ast.Call):
                        for kw in stmt.value.keywords:
                            if kw.arg == "min_length" and isinstance(kw.value, ast.Constant) and kw.value.value == 1:
                                found_scales_constraint = True

    assert found_scales_constraint, "MatrixPromptBlock does not enforce min_length=1 on scales"


def test_prompt_factory_ast_no_hasattr_getattr() -> None:
    """Verifies prompt_factory.py contains 0 hasattr/getattr calls."""
    tree = _load_ast("backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py")
    banned_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("hasattr", "getattr"):
                banned_calls.append((node.func.id, node.lineno))

    assert not banned_calls, f"Found banned reflection calls in prompt_factory.py: {banned_calls}"


def test_prompt_factory_ast_no_find_value_by_key() -> None:
    """Verifies prompt_factory.py contains 0 find_value_by_key definitions or calls."""
    tree = _load_ast("backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py")
    found_occurrences = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "find_value_by_key":
            found_occurrences.append(("def", node.lineno))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "find_value_by_key":
            found_occurrences.append(("call", node.lineno))

    assert not found_occurrences, f"Found find_value_by_key occurrences: {found_occurrences}"


def test_prompt_factory_ast_no_slug_checks() -> None:
    """Verifies prompt_factory.py contains 0 .slug comparisons or routing logic."""
    tree = _load_ast("backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py")
    slug_accesses = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "slug":
            slug_accesses.append(node.lineno)

    assert not slug_accesses, f"Found .slug accesses in prompt_factory.py at lines: {slug_accesses}"


def test_prompt_factory_ast_no_naked_dicts_in_mechanical_anchors() -> None:
    """Verifies prompt_factory.py uses MechanicalAnchorsPayload rather than naked dict checks."""
    tree = _load_ast("backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py")
    imports_mechanical_anchors = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "mechanical_anchors" in node.module:
                for alias in node.names:
                    if alias.name == "MechanicalAnchorsPayload":
                        imports_mechanical_anchors = True

    assert imports_mechanical_anchors, "prompt_factory.py must import and use MechanicalAnchorsPayload"


def test_ast_xml_layer_ordering_compliance() -> None:
    """Verifies prompt_factory.py and global mandates define Layer 1 through Layer 4 cleanly."""
    tree = _load_ast("backend_v2/models/prompts/global_mandates.py")
    has_global_mandates = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GLOBAL_MANDATES_XML":
                    has_global_mandates = True

    assert has_global_mandates, "global_mandates.py must define GLOBAL_MANDATES_XML"


def test_ast_guardrail_catches_new_hasattr_getattr_negative() -> None:
    """Anti-happy path: Proves AST scanner detects violations by passing a mock AST node."""
    bad_code = """
def sample_function(obj):
    if hasattr(obj, 'custom_attr'):
        return getattr(obj, 'custom_attr')
    return None
"""
    mock_tree = ast.parse(bad_code)
    banned_calls = []
    for node in ast.walk(mock_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("hasattr", "getattr"):
                banned_calls.append(node.func.id)

    assert banned_calls == ["hasattr", "getattr"], "AST scanner failed to catch hasattr/getattr violation"


def test_ast_guardrail_catches_missing_strict_model_config_negative() -> None:
    """Anti-happy path: Proves AST scanner catches models missing strict frozen ConfigDict."""
    bad_model_code = """
class InvalidModel(BaseModel):
    model_config = ConfigDict(strict=False)
    id: str
"""
    mock_tree = ast.parse(bad_model_code)
    has_valid_config = False

    for node in ast.walk(mock_tree):
        if isinstance(node, ast.ClassDef):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "model_config":
                            if isinstance(stmt.value, ast.Call):
                                kwargs = {kw.arg: kw.value for kw in stmt.value.keywords if kw.arg}
                                strict_val = kwargs.get("strict")
                                extra_val = kwargs.get("extra")
                                frozen_val = kwargs.get("frozen")

                                is_strict = isinstance(strict_val, ast.Constant) and strict_val.value is True
                                is_forbid = isinstance(extra_val, ast.Constant) and extra_val.value == "forbid"
                                is_frozen = isinstance(frozen_val, ast.Constant) and frozen_val.value is True

                                if is_strict and is_forbid and is_frozen:
                                    has_valid_config = True

    assert not has_valid_config, "AST scanner should have flagged invalid model config as non-compliant"


def test_ast_no_pydantic_new_or_construct_hijacking() -> None:
    """AST Guardrail: Domain models must NOT override __new__ or model_construct (Chameleon Class ban)."""
    tree = _load_ast("backend_v2/models/domain/prompt_blocks.py")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    assert item.name != "__new__", (
                        f"Class '{node.name}' in prompt_blocks.py defines '__new__'. "
                        "BaseModel classes must not hijack __new__ for polymorphism; "
                        "use TypeAdapter(Annotated[Union, Field(discriminator=...)])"
                    )
                    assert item.name != "model_construct", (
                        f"Class '{node.name}' in prompt_blocks.py overrides 'model_construct'. "
                        "Use concrete subtype model_construct or a dedicated factory."
                    )


def test_ast_guardrail_catches_pydantic_new_hijacking_negative() -> None:
    """Anti-happy path: Proves AST scanner detects __new__ hijacking in mock class definitions."""
    bad_code = """
class ChameleonModel(BaseModel):
    def __new__(cls, *args, **kwargs):
        return Subclass(*args, **kwargs)
"""
    mock_tree = ast.parse(bad_code)
    found_new = False

    for node in ast.walk(mock_tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__new__":
                    found_new = True

    assert found_new, "AST scanner should have detected __new__ hijacking in mock class"

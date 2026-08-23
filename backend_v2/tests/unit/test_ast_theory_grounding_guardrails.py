"""AST and Schema Guardrails for Theory Grounding Dual Injection Elimination.

Enforces static AST verification and Seed schema constraints to prevent regression:
1. Matrix prompt blocks in seed_data.json must not have duplicate epistemic citation tails.
2. All 13 matrix blocks must have fully populated TheoryGrounding structures.
3. MatrixSensorPromptBuilder AST must use pure citation_reference without raw JSON/URL dumping.
4. SourceVerificationHook must be properly registered and free of mock API keys.
"""

import ast
import json
from pathlib import Path


def test_seed_matrices_have_no_epistemic_anchor_in_ai_description() -> None:
    """TC-AST-01: Asserts that 0 matrix blocks in seed_data.json contain EPISTEMIC ANCHOR: in ai_description."""
    seed_file = Path("backend_v2/seed/seed_data.json")
    assert seed_file.exists(), "seed_data.json not found"

    with seed_file.open(encoding="utf-8") as f:
        data = json.load(f)

    matrix_blocks = [b for b in data.get("prompt_blocks", []) if b.get("category_id") == "matrix"]
    assert len(matrix_blocks) == 13, f"Expected 13 matrix blocks, found {len(matrix_blocks)}"

    for b in matrix_blocks:
        ai_desc = b.get("ai_description", "")
        assert "EPISTEMIC ANCHOR:" not in ai_desc, (
            f"Matrix block {b['id']} still contains EPISTEMIC ANCHOR: in ai_description"
        )


def test_seed_matrices_have_valid_theory_grounding() -> None:
    """TC-AST-02: Asserts that all 13 matrix blocks have non-null theory_grounding with valid URL and citation."""
    seed_file = Path("backend_v2/seed/seed_data.json")
    with seed_file.open(encoding="utf-8") as f:
        data = json.load(f)

    matrix_blocks = [b for b in data.get("prompt_blocks", []) if b.get("category_id") == "matrix"]
    for b in matrix_blocks:
        tg = b.get("theory_grounding")
        assert tg is not None, f"Matrix block {b['id']} is missing theory_grounding"
        assert isinstance(tg, dict), f"Matrix block {b['id']} theory_grounding is not a dict"
        assert tg.get("source_url"), f"Matrix block {b['id']} theory_grounding missing source_url"
        assert tg.get("citation_reference"), f"Matrix block {b['id']} theory_grounding missing citation_reference"


def test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation() -> None:
    """TC-AST-03: Inspects AST of MatrixSensorPromptBuilder to verify pure citation_reference usage."""
    source_file = Path("backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py")
    assert source_file.exists(), "matrix_sensor_prompt_builder.py not found"

    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))

    # Verify that model_dump_json is never called on theory_grounding
    found_model_dump_json = False
    found_citation_reference = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr == "model_dump_json":
                found_model_dump_json = True
            if node.attr == "citation_reference":
                found_citation_reference = True

    assert not found_model_dump_json, "MatrixSensorPromptBuilder AST contains banned model_dump_json call"
    assert found_citation_reference, "MatrixSensorPromptBuilder AST must reference theory_grounding.citation_reference"


def test_source_verification_hook_registered_and_safe() -> None:
    """TC-AST-04: Inspects AST of source_verification_hook.py to verify decorator and no hardcoded mock API keys."""
    source_file = Path("backend_v2/hooks/source_verification_hook.py")
    assert source_file.exists(), "source_verification_hook.py not found"

    content = source_file.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(source_file))

    # Check decorator
    found_hook_decorator = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "source_verification_hook":
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.attr == "register":
                        found_hook_decorator = True

    assert found_hook_decorator, "source_verification_hook must be decorated with @hook_registry.register"
    assert 'api_key="mock"' not in content, "source_verification_hook.py must not contain hardcoded mock API keys"

"""AST Architectural Guardrail Tests for Matrix & Workflow Scale Decoupling.

Enforces:
1. PromptBlock in backend_v2/models/v2_core.py has NO scale_min or scale_max attributes.
2. OutputProfile in backend_v2/models/v2_core.py HAS custom_scale_min and custom_scale_max attributes.
3. seed_data.json has NO scale_min or scale_max attributes across all prompt_blocks.
"""

import ast
import json
from pathlib import Path


def _get_class_node_from_file(file_path: Path, class_name: str) -> ast.ClassDef | None:
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def test_prompt_block_has_no_scale_min_or_max() -> None:
    """AST Guardrail: PromptBlock in v2_core.py must NOT have scale_min or scale_max fields."""
    v2_core_path = Path("backend_v2/models/v2_core.py")
    assert v2_core_path.exists(), f"File {v2_core_path} does not exist"

    class_node = _get_class_node_from_file(v2_core_path, "PromptBlock")
    assert class_node is not None, "PromptBlock class not found in v2_core.py"

    field_names: set[str] = set()
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field_names.add(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    field_names.add(target.id)

    assert "scale_min" not in field_names, "PromptBlock must NOT contain 'scale_min' field"
    assert "scale_max" not in field_names, "PromptBlock must NOT contain 'scale_max' field"
    assert "computed_min" in field_names, "PromptBlock must retain derived 'computed_min' field"
    assert "computed_max" in field_names, "PromptBlock must retain derived 'computed_max' field"


def test_output_profile_has_custom_scale_bounds() -> None:
    """AST Guardrail: OutputProfile in v2_core.py MUST have custom_scale_min and custom_scale_max fields."""
    v2_core_path = Path("backend_v2/models/v2_core.py")
    assert v2_core_path.exists(), f"File {v2_core_path} does not exist"

    class_node = _get_class_node_from_file(v2_core_path, "OutputProfile")
    assert class_node is not None, "OutputProfile class not found in v2_core.py"

    field_names: set[str] = set()
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field_names.add(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    field_names.add(target.id)

    assert "custom_scale_min" in field_names, "OutputProfile MUST contain 'custom_scale_min' field"
    assert "custom_scale_max" in field_names, "OutputProfile MUST contain 'custom_scale_max' field"


def test_seed_data_matrices_have_no_scale_min_or_max() -> None:
    """Seed Vault Guardrail: seed_data.json prompt_blocks must NOT contain scale_min or scale_max."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    assert seed_path.exists(), f"File {seed_path} does not exist"

    seed_data = json.loads(seed_path.read_text(encoding="utf-8"))
    prompt_blocks = seed_data.get("prompt_blocks", [])
    assert len(prompt_blocks) > 0, "seed_data.json must contain prompt_blocks"

    for pb in prompt_blocks:
        pb_id = pb.get("id", "<unknown>")
        assert "scale_min" not in pb, f"PromptBlock '{pb_id}' in seed_data.json must NOT contain 'scale_min'"
        assert "scale_max" not in pb, f"PromptBlock '{pb_id}' in seed_data.json must NOT contain 'scale_max'"

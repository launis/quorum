"""AST Guardrail Test Suite for Engine Dispatch, Decoupling & Grounding Resilience (EPIC-147).

Enforces 5 core architectural invariants via static AST node parsing:
1. Hook Registration & API Key Safety (Source verification hook registered, zero hardcoded API keys).
2. Procedural String Routing Elimination (DAGExecutor routes via Enum keys, zero procedural string routing).
3. Frozen Context Immutability (Zero in-place mutations of frozen_ctx.generated_schemas in strategies).
4. Prompt Block Repository Set Parity (Strict mathematical set difference and Fail-Fast missing resolution).
5. Hook State Immutability (Zero in-place mutations of hook_state.metadata/inputs across strategies & hooks).

Includes explicit negative test functions per ki_ast_guardrail_testing.md to prove scanner resilience.
"""

import ast
from pathlib import Path
from typing import Any


class HookRegistrationVisitor(ast.NodeVisitor):
    """AST visitor to verify hook registration and ensure no hardcoded API keys exist."""

    def __init__(self) -> None:
        self.is_registered: bool = False
        self.registered_names: list[str] = []
        self.hardcoded_keys: list[str] = []

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_decorators(node.decorator_list)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_decorators(node.decorator_list)
        self.generic_visit(node)

    def _check_decorators(self, decorators: list[ast.expr]) -> None:
        for dec in decorators:
            if isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute) and func.attr == "register":
                    if isinstance(func.value, ast.Name) and func.value.id == "hook_registry":
                        self.is_registered = True
                        for arg in dec.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                self.registered_names.append(arg.value)
                elif isinstance(func, ast.Name) and func.id == "register":
                    self.is_registered = True
            elif isinstance(dec, ast.Attribute) and dec.attr == "register":
                if isinstance(dec.value, ast.Name) and dec.value.id == "hook_registry":
                    self.is_registered = True

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            val = node.value.strip()
            # Detect typical hardcoded credential patterns (e.g. tvly-*, sk-*, AIza*, mock-key-*)
            if val.startswith(("tvly-", "sk-", "AIza", "key-", "mock-key-", "secret-")) or (
                len(val) >= 20 and "secret" in val.lower()
            ):
                self.hardcoded_keys.append(val)
        self.generic_visit(node)


def scan_code_for_hook_registration(code: str) -> dict[str, Any]:
    """Scans Python code for hook registration and hardcoded keys."""
    tree = ast.parse(code)
    visitor = HookRegistrationVisitor()
    visitor.visit(tree)
    return {
        "is_registered": visitor.is_registered,
        "registered_names": visitor.registered_names,
        "has_hardcoded_keys": len(visitor.hardcoded_keys) > 0,
        "hardcoded_keys": visitor.hardcoded_keys,
    }


def scan_file_for_hook_registration(filepath: Path) -> dict[str, Any]:
    """Scans a file for hook registration and hardcoded keys."""
    if not filepath.exists():
        return {
            "is_registered": False,
            "registered_names": [],
            "has_hardcoded_keys": False,
            "hardcoded_keys": [],
        }
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_hook_registration(code)


class DagExecutorRoutingVisitor(ast.NodeVisitor):
    """AST visitor to assert zero procedural string routing on step types."""

    def __init__(self) -> None:
        self.procedural_string_comparisons: list[str] = []
        self.uses_step_type_enum: bool = False

    def visit_Compare(self, node: ast.Compare) -> None:
        # Detect step.type == "logic" or step_def.type == "llm" procedural string routing
        left = node.left
        is_type_attr = False
        if isinstance(left, ast.Attribute) and left.attr == "type":
            is_type_attr = True

        if is_type_attr:
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    if comparator.value in ("logic", "llm", "synthesis", "tda", "prompt"):
                        self.procedural_string_comparisons.append(comparator.value)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == "StepType":
            if node.attr in ("LLM", "LOGIC"):
                self.uses_step_type_enum = True
        self.generic_visit(node)


def scan_code_for_dag_routing(code: str) -> dict[str, Any]:
    """Scans Python code for procedural string routing violations."""
    tree = ast.parse(code)
    visitor = DagExecutorRoutingVisitor()
    visitor.visit(tree)
    return {
        "has_procedural_string_routing": len(visitor.procedural_string_comparisons) > 0,
        "procedural_string_comparisons": visitor.procedural_string_comparisons,
        "uses_step_type_enum": visitor.uses_step_type_enum,
    }


def scan_file_for_dag_routing(filepath: Path) -> dict[str, Any]:
    """Scans a file for procedural string routing violations."""
    if not filepath.exists():
        return {
            "has_procedural_string_routing": False,
            "procedural_string_comparisons": [],
            "uses_step_type_enum": False,
        }
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_dag_routing(code)


class FrozenContextMutationVisitor(ast.NodeVisitor):
    """AST visitor to detect in-place mutations of frozen_ctx.generated_schemas."""

    def __init__(self) -> None:
        self.has_generated_schemas_mutation: bool = False

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_targets(node.targets)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_targets([node.target])
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_targets([node.target])
        self.generic_visit(node)

    def _check_targets(self, targets: list[ast.expr]) -> None:
        for target in targets:
            if isinstance(target, ast.Subscript):
                val = target.value
                if isinstance(val, ast.Attribute) and val.attr == "generated_schemas":
                    self.has_generated_schemas_mutation = True
            elif isinstance(target, ast.Attribute) and target.attr == "generated_schemas":
                self.has_generated_schemas_mutation = True

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("update", "setdefault", "pop", "clear"):
                val = node.func.value
                if isinstance(val, ast.Attribute) and val.attr == "generated_schemas":
                    self.has_generated_schemas_mutation = True
        self.generic_visit(node)


def scan_code_for_frozen_ctx_mutations(code: str) -> dict[str, Any]:
    """Scans code for frozen context in-place mutation violations."""
    tree = ast.parse(code)
    visitor = FrozenContextMutationVisitor()
    visitor.visit(tree)
    return {
        "has_frozen_ctx_generated_schemas_mutation": visitor.has_generated_schemas_mutation,
    }


def scan_file_for_frozen_ctx_mutations(filepath: Path) -> dict[str, Any]:
    """Scans a file for frozen context in-place mutation violations."""
    if not filepath.exists():
        return {"has_frozen_ctx_generated_schemas_mutation": False}
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_frozen_ctx_mutations(code)


class PromptBlockRepoSetParityVisitor(ast.NodeVisitor):
    """AST visitor to verify mathematical set difference validation in PromptBlockRepository."""

    def __init__(self) -> None:
        self.has_set_difference_check: bool = False
        self.raises_app_exception_on_missing: bool = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node.name == "get_prompt_blocks_by_ids":
            self._inspect_get_prompt_blocks_by_ids(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == "get_prompt_blocks_by_ids":
            self._inspect_get_prompt_blocks_by_ids(node)
        self.generic_visit(node)

    def _inspect_get_prompt_blocks_by_ids(self, func_node: ast.AST) -> None:
        for inner in ast.walk(func_node):
            # Check for set difference: e.g. unique_ids - found_ids or comprehension checking missing_ids
            if isinstance(inner, ast.BinOp) and isinstance(inner.op, ast.Sub):
                self.has_set_difference_check = True
            elif isinstance(inner, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
                for gen in inner.generators:
                    for if_expr in gen.ifs:
                        if isinstance(if_expr, ast.Compare):
                            for op in if_expr.ops:
                                if isinstance(op, ast.NotIn):
                                    self.has_set_difference_check = True

            # Check for AppException raise on missing
            if isinstance(inner, ast.Raise):
                if isinstance(inner.exc, ast.Call):
                    func = inner.exc.func
                    if isinstance(func, ast.Name) and func.id == "AppException":
                        self.raises_app_exception_on_missing = True
                    elif isinstance(func, ast.Attribute) and func.attr == "AppException":
                        self.raises_app_exception_on_missing = True


def scan_code_for_prompt_block_repo_set_parity(code: str) -> dict[str, Any]:
    """Scans code for PromptBlock repository mathematical set difference validation."""
    tree = ast.parse(code)
    visitor = PromptBlockRepoSetParityVisitor()
    visitor.visit(tree)
    return {
        "has_set_difference_check": visitor.has_set_difference_check,
        "raises_app_exception_on_missing": visitor.raises_app_exception_on_missing,
    }


def scan_file_for_prompt_block_repo_set_parity(filepath: Path) -> dict[str, Any]:
    """Scans a file for PromptBlock repository mathematical set difference validation."""
    if not filepath.exists():
        return {
            "has_set_difference_check": False,
            "raises_app_exception_on_missing": False,
        }
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_prompt_block_repo_set_parity(code)


class HookStateImmutabilityVisitor(ast.NodeVisitor):
    """AST visitor to assert zero in-place mutations of hook_state.metadata or hook_state.inputs."""

    def __init__(self) -> None:
        self.has_inplace_metadata_mutation: bool = False
        self.has_inplace_inputs_mutation: bool = False

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_targets(node.targets)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_targets([node.target])
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_targets([node.target])
        self.generic_visit(node)

    def _check_targets(self, targets: list[ast.expr]) -> None:
        for target in targets:
            if isinstance(target, ast.Subscript):
                val = target.value
                if isinstance(val, ast.Attribute):
                    target_obj_name = getattr(val.value, "id", "")
                    if target_obj_name in ("state", "hook_state"):
                        if val.attr == "metadata":
                            self.has_inplace_metadata_mutation = True
                        elif val.attr == "inputs":
                            self.has_inplace_inputs_mutation = True

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("update", "setdefault", "pop", "clear"):
                val = node.func.value
                if isinstance(val, ast.Attribute):
                    target_obj_name = getattr(val.value, "id", "")
                    if target_obj_name in ("state", "hook_state"):
                        if val.attr == "metadata":
                            self.has_inplace_metadata_mutation = True
                        elif val.attr == "inputs":
                            self.has_inplace_inputs_mutation = True
        self.generic_visit(node)


def scan_code_for_hook_state_immutability(code: str) -> dict[str, Any]:
    """Scans code for in-place HookState mutations."""
    tree = ast.parse(code)
    visitor = HookStateImmutabilityVisitor()
    visitor.visit(tree)
    return {
        "has_inplace_metadata_mutation": visitor.has_inplace_metadata_mutation,
        "has_inplace_inputs_mutation": visitor.has_inplace_inputs_mutation,
    }


def scan_file_for_hook_state_immutability(filepath: Path) -> dict[str, Any]:
    """Scans a file for in-place HookState mutations."""
    if not filepath.exists():
        return {
            "has_inplace_metadata_mutation": False,
            "has_inplace_inputs_mutation": False,
        }
    code = filepath.read_text(encoding="utf-8")
    return scan_code_for_hook_state_immutability(code)


# ==============================================================================
# Positive Tests: Live Codebase Invariant Verification
# ==============================================================================


def test_source_verification_hook_registered_and_safe() -> None:
    """Verify source_verification_hook is registered with hook_registry and contains no hardcoded API keys."""
    hook_file = Path("backend_v2/hooks/source_verification_hook.py")
    assert hook_file.exists(), f"Missing target hook file: {hook_file}"

    res = scan_file_for_hook_registration(hook_file)
    assert res["is_registered"] is True, f"Hook {hook_file} is not registered with @hook_registry.register"
    assert "source_verification_hook" in res["registered_names"] or "source_verification" in res["registered_names"], (
        "Hook registration name must be 'source_verification_hook' or 'source_verification'"
    )
    assert res["has_hardcoded_keys"] is False, f"Hardcoded API keys detected in {hook_file}: {res['hardcoded_keys']}"


def test_node_strategy_registry_ast_has_no_procedural_string_routing() -> None:
    """Verify dag_executor.py contains zero procedural string comparisons for step types."""
    dag_file = Path("backend_v2/services/orchestrator/dag_executor.py")
    assert dag_file.exists(), f"Missing target file: {dag_file}"

    res = scan_file_for_dag_routing(dag_file)
    assert res["has_procedural_string_routing"] is False, (
        f"Procedural string routing found in {dag_file}: {res['procedural_string_comparisons']}"
    )
    assert res["uses_step_type_enum"] is True, f"{dag_file} must utilize StepType enum for dispatch"


def test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation() -> None:
    """Verify LLMNodeStrategy in llm.py contains zero in-place mutations of frozen_ctx.generated_schemas."""
    strategy_file = Path("backend_v2/services/orchestrator/strategies/llm.py")
    assert strategy_file.exists(), f"Missing strategy file: {strategy_file}"

    res = scan_file_for_frozen_ctx_mutations(strategy_file)
    assert res["has_frozen_ctx_generated_schemas_mutation"] is False, (
        f"Forbidden in-place mutation of frozen_ctx.generated_schemas found in {strategy_file}"
    )


def test_prompt_block_repo_ast_strict_missing_parity() -> None:
    """Verify PromptBlockRepositoryImpl enforces mathematical set difference and raises AppException on missing."""
    repo_file = Path("backend_v2/database/repositories/components/prompt_block.py")
    assert repo_file.exists(), f"Missing repo file: {repo_file}"

    res = scan_file_for_prompt_block_repo_set_parity(repo_file)
    assert res["has_set_difference_check"] is True, (
        f"{repo_file} must perform mathematical set difference validation on requested prompt block IDs"
    )
    assert res["raises_app_exception_on_missing"] is True, (
        f"{repo_file} must raise AppException when strict=True and prompt block IDs are missing"
    )


def test_hook_state_immutability_and_no_inplace_metadata_mutation() -> None:
    """Verify strategies/llm.py and hooks/ contain zero in-place mutations of hook_state.metadata/inputs."""
    strategy_file = Path("backend_v2/services/orchestrator/strategies/llm.py")
    res_strategy = scan_file_for_hook_state_immutability(strategy_file)
    assert res_strategy["has_inplace_metadata_mutation"] is False, (
        f"In-place metadata mutation found in {strategy_file}"
    )
    assert res_strategy["has_inplace_inputs_mutation"] is False, f"In-place inputs mutation found in {strategy_file}"

    hooks_dir = Path("backend_v2/hooks")
    if hooks_dir.exists():
        for hook_path in hooks_dir.rglob("*.py"):
            res_hook = scan_file_for_hook_state_immutability(hook_path)
            assert res_hook["has_inplace_metadata_mutation"] is False, (
                f"In-place metadata mutation found in {hook_path}"
            )
            assert res_hook["has_inplace_inputs_mutation"] is False, f"In-place inputs mutation found in {hook_path}"


# ==============================================================================
# Negative Tests: Anti-Happy-Path Scanner Verification (ki_ast_guardrail_testing.md)
# ==============================================================================


def test_ast_guardrails_detect_unregistered_hook_negative() -> None:
    """Negative test: verify scanner detects missing registration and hardcoded keys."""
    unregistered_code = """
async def my_unregistered_hook(state, deps):
    api_key = "tvly-secret_key_12345"
    return {"success": True}
"""
    res = scan_code_for_hook_registration(unregistered_code)
    assert res["is_registered"] is False
    assert res["has_hardcoded_keys"] is True
    assert "tvly-secret_key_12345" in res["hardcoded_keys"]


def test_ast_guardrails_detect_procedural_string_routing_negative() -> None:
    """Negative test: verify scanner detects procedural string comparison violations."""
    violating_code = """
async def execute_node(step, step_def):
    if step_def.type == "logic":
        return await do_logic()
    elif step_def.type == "llm":
        return await do_llm()
"""
    res = scan_code_for_dag_routing(violating_code)
    assert res["has_procedural_string_routing"] is True
    assert "logic" in res["procedural_string_comparisons"]
    assert "llm" in res["procedural_string_comparisons"]


def test_ast_guardrails_detect_inplace_schema_mutation_negative() -> None:
    """Negative test: verify scanner detects in-place frozen_ctx.generated_schemas mutations."""
    violating_subscript_code = """
async def execute(context, frozen_ctx):
    frozen_ctx.generated_schemas["schema_id"] = {"type": "object"}
"""
    res_sub = scan_code_for_frozen_ctx_mutations(violating_subscript_code)
    assert res_sub["has_frozen_ctx_generated_schemas_mutation"] is True

    violating_update_code = """
async def execute(context, frozen_ctx):
    frozen_ctx.generated_schemas.update({"schema_id": {"type": "object"}})
"""
    res_upd = scan_code_for_frozen_ctx_mutations(violating_update_code)
    assert res_upd["has_frozen_ctx_generated_schemas_mutation"] is True


def test_ast_guardrails_detect_missing_set_parity_negative() -> None:
    """Negative test: verify scanner detects missing set difference and missing exception in repository."""
    flawed_repo_code = """
class FlawedRepo:
    async def get_prompt_blocks_by_ids(self, block_ids: list[str], strict: bool = True):
        results = []
        for bid in block_ids:
            doc = await self.get(bid)
            if doc:
                results.append(doc)
        return results
"""
    res = scan_code_for_prompt_block_repo_set_parity(flawed_repo_code)
    assert res["has_set_difference_check"] is False
    assert res["raises_app_exception_on_missing"] is False


def test_ast_guardrails_detect_inplace_hook_state_mutation_negative() -> None:
    """Negative test: verify scanner detects in-place mutations of hook_state.metadata or state.inputs."""
    violating_metadata_code = """
async def run_hook(hook_state, deps):
    hook_state.metadata["injected_key"] = "forbidden_value"
    return HookResult(success=True)
"""
    res_meta = scan_code_for_hook_state_immutability(violating_metadata_code)
    assert res_meta["has_inplace_metadata_mutation"] is True
    assert res_meta["has_inplace_inputs_mutation"] is False

    violating_inputs_code = """
async def run_hook(state, deps):
    state.inputs["mutated_key"] = "forbidden_value"
    return HookResult(success=True)
"""
    res_inputs = scan_code_for_hook_state_immutability(violating_inputs_code)
    assert res_inputs["has_inplace_inputs_mutation"] is True
    assert res_inputs["has_inplace_metadata_mutation"] is False

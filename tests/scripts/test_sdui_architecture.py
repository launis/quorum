import ast
import os
from pathlib import Path
import pytest

def audit_file(filepath: str) -> list[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    violations = []
    
    # 1. Module-level dictionary ending in _RULES
    rules_dicts = []
    classes = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith('_RULES'):
                    rules_dicts.append(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id.endswith('_RULES'):
                rules_dicts.append(node.target.id)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)

    if not rules_dicts:
        violations.append("[KI_SDUI_ADAPTER_PATTERN] Missing module-level dictionary ending in _RULES.")
    
    if len(classes) != 1:
        violations.append(f"[KI_SDUI_ADAPTER_PATTERN] Expected exactly one class, found {len(classes)}.")
    
    if not classes:
        return violations # Can't check class-level stuff if there are no classes
        
    adapter_class = classes[0]
    
    # 2. Check locked terminology: @staticmethod and def build(context: AdapterContext) -> list[AnySduiBlock]
    build_method = None
    for node in adapter_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'build':
            build_method = node
            break
            
    if not build_method:
        violations.append("[KI_SDUI_ADAPTER_PATTERN] Missing `build` method in the adapter class.")
    else:
        # Check staticmethod
        is_static = any(
            isinstance(d, ast.Name) and d.id == 'staticmethod' 
            for d in build_method.decorator_list
        )
        if not is_static:
            violations.append("[KI_SDUI_ADAPTER_PATTERN] `build` method is missing `@staticmethod` decorator.")
            
        # Check signature: context: AdapterContext
        args = build_method.args.args
        if len(args) != 1 or not (args[0].arg == 'context' and getattr(args[0].annotation, 'id', '') == 'AdapterContext'):
            violations.append("[KI_SDUI_ADAPTER_PATTERN] `build` method must accept exactly `context: AdapterContext`.")
            
        # Check return type: list[AnySduiBlock]
        returns = build_method.returns
        is_list = False
        if isinstance(returns, ast.Subscript):
            if getattr(returns.value, 'id', '') == 'list':
                if getattr(returns.slice, 'id', '') == 'AnySduiBlock':
                    is_list = True
        if not is_list:
            violations.append("[KI_SDUI_ADAPTER_PATTERN] `build` method return type must be `list[AnySduiBlock]`.")
            
    class RuleVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Call(self, node):
            # Check for .get() on RULES
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'get':
                if isinstance(node.func.value, ast.Name) and node.func.value.id.endswith('_RULES'):
                    self.violations.append(f"[KI_SDUI_ADAPTER_PATTERN] Fail-fast violation: Used .get() on {node.func.value.id} at line {node.lineno}.")
            
            # Check for God method leaks (business logic)
            func_id = getattr(node.func, 'id', '')
            if func_id in ('min', 'max', 'sum', 'round'):
                self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] God Method leak: SDUI Adapters must be dumb painters and must not perform mathematical calculations like `{func_id}()` at line {node.lineno}.")
            
            # Very basic checks for DB lookups or models
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in ('db', 'session', 'repository', 'llm'):
                        self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] God Method leak: Direct IO or DB lookup `{node.func.value.id}.{node.func.attr}` at line {node.lineno}.")
            
            self.generic_visit(node)

        def visit_BinOp(self, node):
            if isinstance(node.op, (ast.Mult, ast.Div, ast.Sub)):
                self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] Business Logic leak: SDUI Adapters must not perform mathematical operations (*, /, -) at line {node.lineno}.")
            self.generic_visit(node)
            
        def visit_ImportFrom(self, node):
            if node.module and any(forbidden in node.module for forbidden in ('utils.scoring', 'orchestrator', 'llm', 'repository', 'api')):
                self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] Business Logic leak: SDUI Adapters must not import from Domain Engines or IO layers (`{node.module}`) at line {node.lineno}.")
            self.generic_visit(node)
            
        def visit_Attribute(self, node):
            if node.attr in ('computed_min', 'computed_max'):
                self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] Banned pattern: SDUI Adapters must be dumb painters and must not perform domain math bounds calculation using `{node.attr}` at line {node.lineno}.")
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id == 'blocks_by_id':
                self.violations.append(f"[KI_TRIPARTITE_PIPELINE_ARCHITECTURE] Banned pattern: SDUI Adapters must not perform raw database/ontology lookups using `{node.id}` at line {node.lineno}.")
            self.generic_visit(node)
            
        def visit_Compare(self, node):
            if len(node.ops) > 0 and isinstance(node.ops[0], ast.In):
                for comp in node.comparators:
                    if isinstance(comp, ast.Name) and comp.id.endswith('_RULES'):
                        self.violations.append(f"[KI_SDUI_ADAPTER_PATTERN] Fail-fast violation: Used `in` operator on {comp.id} at line {node.lineno}.")
            self.generic_visit(node)
            
        def visit_ExceptHandler(self, node):
            is_key_error = False
            if isinstance(node.type, ast.Name) and node.type.id == 'KeyError':
                is_key_error = True
            elif isinstance(node.type, ast.Tuple):
                if any(isinstance(elt, ast.Name) and elt.id == 'KeyError' for elt in node.type.elts):
                    is_key_error = True
                    
            if is_key_error:
                has_logger_error = False
                has_raise_app_exception = False
                for body_node in node.body:
                    if isinstance(body_node, ast.Expr) and isinstance(body_node.value, ast.Call):
                        call = body_node.value
                        if isinstance(call.func, ast.Attribute) and getattr(call.func.value, 'id', '') == 'logger' and call.func.attr == 'error':
                            if any(kw.arg == 'exc_info' and isinstance(kw.value, ast.Constant) and kw.value.value == True for kw in call.keywords):
                                has_logger_error = True
                    if isinstance(body_node, ast.Raise):
                        if isinstance(body_node.exc, ast.Call) and getattr(body_node.exc.func, 'id', '') == 'AppException':
                            has_raise_app_exception = True
                            
                if not (has_logger_error and has_raise_app_exception):
                    self.violations.append(f"[KI_SDUI_ADAPTER_PATTERN] Dual Logging violation: KeyError handler at line {node.lineno} does not `logger.error(..., exc_info=True)` followed by `raise AppException(...)`.")

            self.generic_visit(node)

    visitor = RuleVisitor()
    visitor.visit(tree)
    violations.extend(visitor.violations)
    
    return violations

def get_adapter_files():
    base_dir = Path("backend_v2/services/sdui/adapters")
    if not base_dir.exists():
        return []
    
    return [
        str(p) for p in base_dir.glob("*.py")
        if p.name not in ("__init__.py", "base_adapter.py")
    ]

@pytest.mark.parametrize("filepath", get_adapter_files())
def test_sdui_adapter_architecture_compliance(filepath: str):
    """
    Enforces the Tripartite Pipeline Architecture (KI_TRIPARTITE_PIPELINE_ARCHITECTURE)
    and Dumb Painter SDUI patterns (KI_SDUI_ADAPTER_PATTERN) across all presentation adapters.
    """
    violations = audit_file(filepath)
    if violations:
        pytest.fail(f"Architectural violations in {filepath}:\n" + "\n".join(violations))

import pathlib
import re

# Fix 1: scripts/night_shift_hardener.py
f = pathlib.Path('scripts/night_shift_hardener.py')
code = f.read_text('utf-8')

old_visit = '''            def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
                import typing
                node = typing.cast(ast.Subscript, self.generic_visit(node))
                # Check for Optional[X] -> X | None
                is_optional = False
                if isinstance(node.value, ast.Name) and node.value.id == "Optional":
                    is_optional = True
                
                if is_optional:
                    return ast.BinOp(
                        left=node.slice,
                        op=ast.BitOr(),
                        right=ast.Constant(value=None)
                    )
                
                # Check for Union[X, Y] -> X | Y
                is_union = False
                if isinstance(node.value, ast.Name) and node.value.id == "Union":
                    is_union = True
                    
                if is_union:
                    if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) >= 2:
                        elements = node.slice.elts
                        res = elements[0]
                        for el in elements[1:]:
                            res = ast.BinOp(left=res, op=ast.BitOr(), right=el)
                        return res
                return node'''

old_visit_2 = '''            def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
                visited_node = self.generic_visit(node)
                # Check for Optional[X] -> X | None
                is_optional = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Optional":
                    is_optional = True
                
                if is_optional:
                    return ast.BinOp(
                        left=getattr(visited_node, "slice", None),
                        op=ast.BitOr(),
                        right=ast.Constant(value=None)
                    )
                
                # Check for Union[X, Y] -> X | Y
                is_union = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Union":
                    is_union = True
                    
                if is_union:
                    if isinstance(getattr(visited_node, "slice", None), ast.Tuple) and len(getattr(visited_node, "slice").elts) >= 2:
                        elements = getattr(visited_node, "slice").elts
                        res = elements[0]
                        for el in elements[1:]:
                            res = ast.BinOp(left=res, op=ast.BitOr(), right=el)
                        return res
                return node'''

new_visit = '''            def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
                import typing
                visited_node = typing.cast(ast.Subscript, self.generic_visit(node))
                # Check for Optional[X] -> X | None
                is_optional = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Optional":
                    is_optional = True
                
                if is_optional:
                    return ast.BinOp(
                        left=typing.cast(ast.expr, getattr(visited_node, "slice", None)),
                        op=ast.BitOr(),
                        right=ast.Constant(value=None)
                    )
                
                # Check for Union[X, Y] -> X | Y
                is_union = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Union":
                    is_union = True
                    
                if is_union:
                    if isinstance(getattr(visited_node, "slice", None), ast.Tuple) and len(getattr(visited_node, "slice").elts) >= 2:
                        elements = getattr(visited_node, "slice").elts
                        res = elements[0]
                        for el in elements[1:]:
                            res = ast.BinOp(left=res, op=ast.BitOr(), right=el)
                        return typing.cast(ast.AST, res)
                return visited_node'''

if old_visit in code:
    code = code.replace(old_visit, new_visit)
if old_visit_2 in code:
    code = code.replace(old_visit_2, new_visit)

f.write_text(code, 'utf-8')

# Fix 2: backend_v2/tests/unit/test_night_shift_hardener.py
f = pathlib.Path('backend_v2/tests/unit/test_night_shift_hardener.py')
code = f.read_text('utf-8')

# Let's ensure setattr is used instead of assignment.
pattern = r'asyncio\.sleep = _mock_sleep[^\n]*'
replacement = r"setattr(asyncio, 'sleep', _mock_sleep)  # type: ignore"
code = re.sub(pattern, replacement, code)
f.write_text(code, 'utf-8')

print("All patched.")

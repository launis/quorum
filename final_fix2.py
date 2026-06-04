import pathlib

# Fix 1: test_scoring.py
f = pathlib.Path('backend_v2/tests/unit/hooks/test_scoring.py')
code = f.read_text('utf-8')
# contextual_override needs to be a boolean, structural_location can be string or none, let's use string.
code = code.replace('"contextual_override": "none"', '"contextual_override": False')
code = code.replace('"structural_location": "none"', '"structural_location": ""')
f.write_text(code, 'utf-8')

# Fix 2: test_epic_61_hardening.py
f = pathlib.Path('backend_v2/tests/unit/test_epic_61_hardening.py')
code = f.read_text('utf-8')
code = code.replace('"json null"', '"return null"')
f.write_text(code, 'utf-8')

print("Fixed again.")

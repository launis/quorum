import os

def replace_in_file(file_path, old_str, new_str):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced in {file_path}")

files = [
    'c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py',
    'c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py',
    'c:/src/quorum/backend_v2/tests/unit/hooks/test_scoring.py'
]

for file in files:
    replace_in_file(file, 
        '"en": "The user is a \'Yes-man\'. Blindly accepted the AI\'s first response."',
        '"en": "The user is a \'Yes-man\'. Blindly accepted the AI\'s first response.", "fi": "Mock"')
    replace_in_file(file, 
        '"en": "No corrective move or objection presented."',
        '"en": "No corrective move or objection presented.", "fi": "Mock"')
    replace_in_file(file, 
        '"en": "The user requested changes, but they were only superficial."',
        '"en": "The user requested changes, but they were only superficial.", "fi": "Mock"')
    replace_in_file(file, 
        'translations": {"en": atom}',
        'translations": {"en": atom, "fi": atom}')


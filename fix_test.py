import sys

with open('backend_v2/tests/unit/test_prompt_compiler.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'msg2 = "CRITICAL: build_blind_evaluation_schema on SALAA POISTETTU! Tämä rikkoo Epic 20 Phase 7 sokeiden kokeilujen arkkitehtuurin."'
replacement = 'msg2 = (\n        "CRITICAL: build_blind_evaluation_schema on SALAA POISTETTU! "\n        "Tämä rikkoo Epic 20 Phase 7 sokeiden kokeilujen arkkitehtuurin."\n    )'

if target in text:
    text = text.replace(target, replacement)
    with open('backend_v2/tests/unit/test_prompt_compiler.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced!")
else:
    print("Target not found.")

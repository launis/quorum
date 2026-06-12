import os
import re

files_to_fix = [
    r'backend_v2/tests/unit/hooks/test_scoring.py',
    r'backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py',
    r'backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_best_of_three.py'
]

for path in files_to_fix:
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*)\{\s*[\'\"]default_locale[\'\"][\s\S]*?[\'\"]en[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"][\s\S]*?\}')
    new_content = pattern.sub(r'\1"\2"', content)

    # We also need to fix the syntax extra bracket issue safely
    # If there is `concept_description: "Something", },` we just replace `, },` with `,` or `}` with nothing if it's trailing.
    pattern2 = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*[\'\"][^\'\"]+[\'\"]\s*,)\s*\},')
    new_content = pattern2.sub(r'\1', new_content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {path}")


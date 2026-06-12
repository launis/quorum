import os
import re

files_to_fix = [
    r'backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_chunk_worker.py',
    r'backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py',
    r'backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py',
    r'backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py',
    r'backend_v2/tests/unit/services/orchestrator/test_causal_analyst_schema.py',
    r'backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py',
    r'backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py',
    r'backend_v2/tests/unit/test_chunk_dlq_fallback_bug.py',
    r'backend_v2/tests/unit/test_epic_61_hardening.py'
]

for path in files_to_fix:
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*[\'\"][^\'\"]+[\'\"]\s*,)\s*\},')
    new_content = pattern.sub(r'\1', content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {path}")

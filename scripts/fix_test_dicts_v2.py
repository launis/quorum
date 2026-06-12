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

def process_file(path):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        content = f.read()


    # We will use simple string replacement since the formatting in tests is usually black-formatted
    # Example format:
    # "concept_description": {
    #     "default_locale": "en",
    #     "translations": {"en": "Atom 1", "fi": "Atom 1"},
    # },
    #
    # or
    # "concept_description": {"default_locale": "en", "translations": {"en": "Atom 1", "fi": "Atom 1"}},

    # regex to match: "concept_description": { ... "en": "SOMETHING" ... }
    # non-greedy match until we find the translation
    pattern = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*)\{\s*[\'\"]default_locale[\'\"][\s\S]*?[\'\"]en[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"][\s\S]*?\}')

    new_content = pattern.sub(r'\1"\2"', content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {path}")

for p in files_to_fix:
    process_file(p)

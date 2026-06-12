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

def replace_in_file(path):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        content = f.read()

    # Pattern for dict-based concept_description or ai_rule_description
    pattern = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*)\{\s*[\'\"]default_locale[\'\"]\s*:\s*[\'\"][^\'\"]+[\'\"]\s*,\s*[\'\"]translations[\'\"]\s*:\s*\{\s*[\'\"][^\'\"]+[\'\"]\s*:\s*[\'\"]([^\'\"]+)[\'\"][^\}]*\}\s*\}')
    content = pattern.sub(r'\1"\2"', content)

    # And there might be I18nText(...) objects
    pattern2 = re.compile(r'(concept_description|ai_rule_description)\s*=\s*I18nText\([^)]*translations\s*=\s*[\'\{]{2}en[\'\"]:\s*[\'\"]([^\'\"]+)[\'\"][^\)]*\)')
    content = pattern2.sub(r'concept_description="\2"', content)

    # And string replacements:
    content = content.replace('.get("en")', '')
    content = content.replace(".get('en')", '')
    content = content.replace('.resolve("en")', '')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {path}")

for path in files_to_fix:
    replace_in_file(path)

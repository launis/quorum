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

    # We also need to fix the syntax extra bracket issue
    pattern2 = re.compile(r'([\'\"](?:concept_description|ai_rule_description)[\'\"]\s*:\s*[\'\"][^\'\"]+[\'\"]\s*,)\s*\},')
    new_content = pattern2.sub(r'\1', new_content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {path}")

# Now fix the python specific mock mock_copy issues
path1 = r'backend_v2/tests/unit/test_chunk_dlq_fallback_bug.py'
if os.path.exists(path1):
    with open(path1, encoding='utf-8') as f:
        content = f.read()
    if 'def model_copy' not in content:
        content = content.replace('class MockChunk:\n    def __init__(self, items):\n        self.items = items\n', 'class MockChunk:\n    def __init__(self, items):\n        self.items = items\n\n    def model_copy(self, update=None):\n        new_items = update.get(\'items\', self.items) if update else self.items\n        return MockChunk(items=new_items)\n')
        with open(path1, 'w', encoding='utf-8') as f:
            f.write(content)

path2 = r'backend_v2/tests/unit/test_epic_61_hardening.py'
if os.path.exists(path2):
    with open(path2, encoding='utf-8') as f:
        content2 = f.read()
    content2 = content2.replace('concept_desc = node.get("concept_description", {})\n                translations = concept_desc.get("translations", {})\n                desc = translations.get("en", "")', 'desc = node.get("concept_description", "")')
    with open(path2, 'w', encoding='utf-8') as f:
        f.write(content2)


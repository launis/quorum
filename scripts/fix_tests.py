import os
import re

files = [
    r'backend_v2/tests/integration/test_lazy_llm_simulation.py',
    r'backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py',
    r'backend_v2/tests/unit/services/orchestrator/test_atomizer.py',
    r'backend_v2/tests/unit/hooks/test_atom_flattening.py'
]

def process_file(filepath):
    if not os.path.exists(filepath):
        print(f'File not found: {filepath}')
        return

    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: replace I18nText
    # concept_description=I18nText(default_locale="en", translations={"en": "something"})
    pattern1 = re.compile(r'(concept_description|ai_rule_description)\s*=\s*I18nText\([^)]*translations\s*=\s*[\'\{]{2}en[\'\"]:\s*[\'\"]([^\'\"]+)[\'\"][^\)]*\)')
    content = pattern1.sub(r'concept_description="\2"', content)

    # Pattern 2: replace ai_rule_description='...'
    pattern2 = re.compile(r'ai_rule_description\s*=\s*([\'\"].*?[\'\"])')
    content = pattern2.sub(r'concept_description=\1', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Processed {filepath}')

for f in files:
    process_file(f)

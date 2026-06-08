import os
import re

files_to_fix = [
    'backend_v2/tests/unit/test_v2_core_strictness.py',
    'backend_v2/tests/integration/test_lazy_llm_simulation.py',
    'backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py',
    'backend_v2/tests/unit/test_schema_builder.py',
    'backend_v2/tests/unit/hooks/test_atom_flattening.py',
    'backend_v2/tests/unit/test_api_prompt_blocks.py',
    'backend_v2/tests/unit/test_api_clone_endpoints.py'
]

for file_path in files_to_fix:
    full_path = os.path.join('c:/src/quorum', file_path)
    with open(full_path, encoding='utf-8') as f:
        content = f.read()

    # Ensure import exists
    if 'PromptBlockCategory' not in content:
        content = re.sub(r'(from backend_v2\.models\.enums import.*?)\n', r'\1, PromptBlockCategory\n', content, count=1)
        if 'PromptBlockCategory' not in content:
            content = 'from backend_v2.models.enums import PromptBlockCategory\n' + content

    # Replace strings with Enum references
    content = content.replace('category_id="system_rule"', 'category_id=PromptBlockCategory.SYSTEM_RULE')
    content = content.replace("category_id='system_rule'", 'category_id=PromptBlockCategory.SYSTEM_RULE')
    content = content.replace('category_id="matrix"', 'category_id=PromptBlockCategory.MATRIX')
    content = content.replace("category_id='matrix'", 'category_id=PromptBlockCategory.MATRIX')

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

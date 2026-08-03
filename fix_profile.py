import glob
import re

for f in glob.glob('backend_v2/tests/unit/services/sdui/adapters/test_matrix_*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('name="test",', 'id="prf_1234567890abcdef", slug="test", workflow_id="wf_123", name=I18nText(en="test"),')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

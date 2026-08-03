import glob
import re

for f in glob.glob('backend_v2/tests/unit/services/sdui/adapters/test_matrix_*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = re.sub(r'I18nText\(en=([^)]+)\)', r'I18nText(default_locale="en", translations={"en": \1})', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

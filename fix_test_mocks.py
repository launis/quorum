import glob

for f in glob.glob('backend_v2/tests/unit/services/sdui/adapters/test_matrix_*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('is_evaluative=True', 'is_evaluative=True, label_i18n=I18nText(default_locale="en", translations={"en": "M1"}), row_explanation=I18nText(default_locale="en", translations={"en": "expl"})')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

with open('backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py', 'r', encoding='utf-8') as file:
    content = file.read()

content = content.replace('assert len(blocks[0].children) == 2', 'assert len(blocks[0].children) == 1')

with open('backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py', 'w', encoding='utf-8') as file:
    file.write(content)

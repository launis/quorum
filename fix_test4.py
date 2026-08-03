import glob

for f in glob.glob('backend_v2/tests/unit/services/sdui/adapters/test_matrix_*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('row_explanation=I18nText(default_locale="en", translations={"en": "expl"})', 'row_explanation="expl"')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

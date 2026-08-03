with open('backend_v2/tests/unit/services/test_blueprint.py', 'r', encoding='utf-8') as file:
    content = file.read()

content = content.replace('== "text_only"]', '== "1d_metrics"]')
content = content.replace("== 'text_only']", "== '1d_metrics']")

with open('backend_v2/tests/unit/services/test_blueprint.py', 'w', encoding='utf-8') as file:
    file.write(content)

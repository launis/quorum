with open('backend_v2/tests/unit/services/test_blueprint.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('layout_0_1d_metrics', 'layout_0_text_only')
content = content.replace('getattr(b, "block_type", "") == "3d_matrix"', 'getattr(b, "block_type", "") == "1d_metrics"')

with open('backend_v2/tests/unit/services/test_blueprint.py', 'w', encoding='utf-8') as f:
    f.write(content)

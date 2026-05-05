import re

with open('c:/src/quorum/backend_v2/tests/unit/test_blueprint.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace "computed_min": 0.0 with "computed_min": 0
content = re.sub(r'"computed_min": \d+\.\d+', lambda m: m.group(0).replace('.0', ''), content)
content = re.sub(r'"computed_max": \d+\.\d+', lambda m: m.group(0).replace('.0', ''), content)

with open('c:/src/quorum/backend_v2/tests/unit/test_blueprint.py', 'w', encoding='utf-8') as f:
    f.write(content)

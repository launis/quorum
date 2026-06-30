import os

paths = [
    'backend_v2/tests/integration/test_lazy_llm_simulation.py',
    'backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    data = data.replace('visual_intent="neutral"', 'visual_intent="info"')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

print('Done fixing visual_intent')

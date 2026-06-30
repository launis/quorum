import os

paths = [
    'backend_v2/tests/integration/test_lazy_llm_simulation.py',
    'backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    # We replace AtomEvaluationItemDTO( with AtomEvaluationItemDTO(chart_display_label="TestLabel", visual_intent="neutral", 
    data = data.replace('AtomEvaluationItemDTO(', 'AtomEvaluationItemDTO(chart_display_label="TestLabel", visual_intent="neutral", ')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
print('Done!')

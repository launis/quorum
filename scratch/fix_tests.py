import re
import uuid

files_to_fix = [
    'backend_v2/tests/integration/test_lazy_llm_simulation.py',
    'backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py'
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replacer(match):
        body = match.group(1)
        if 'visual_intent' not in body:
            if body.strip().endswith(','):
                body += '\n        chart_display_label="TestLabel", visual_intent="neutral"'
            else:
                body += ',\n        chart_display_label="TestLabel", visual_intent="neutral"'
        return 'AtomEvaluationItemDTO(' + body + ')'

    new_content = re.sub(r'AtomEvaluationItemDTO\((.*?)\)', replacer, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print('Done fixing AtomEvaluationItemDTO in tests')

import os

filepath = 'backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py'
with open(filepath, 'r', encoding='utf-8') as f:
    data = f.read()

data = data.replace('structural_location=None', 'structural_location="N/A"')
data = data.replace('structural_location="page 42" if llm_override else None', 'structural_location="page 42" if llm_override else "N/A"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(data)
print("Done")

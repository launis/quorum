import json
with open('c:/src/quorum/old_seed.json', encoding='utf-16') as f:
    data = json.load(f)
for matrix in data.get('target_matrices', []):
    if matrix.get('id') == 'mat_a3e9c4f1d6b2':
        print("synthesis preamble:")
        print(matrix.get('synthesis', {}).get('preamble_text', {}))
        print("synthesis system prompt:")
        print(matrix.get('synthesis', {}).get('system_prompt', {}))

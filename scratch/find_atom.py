import json

def find_atom(d, target, path):
    if isinstance(d, dict):
        for k, v in d.items():
            if target in json.dumps(v):
                return find_atom(v, target, path + [k])
    elif isinstance(d, list):
        for i, v in enumerate(d):
            if target in json.dumps(v):
                return find_atom(v, target, path + [str(i)])
    return path

with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    seed = json.load(f)

print(find_atom(seed['prompt_blocks'], 'tda_aa0b85a7febe4a3d9f580223c36a1646', []))

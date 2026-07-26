import json
with open('c:/src/quorum/old_seed.json', encoding='utf-16') as f:
    data = json.load(f)

def find_dict_with_key(data, key):
    if isinstance(data, dict):
        if key in data:
            yield data[key]
        for k, v in data.items():
            yield from find_dict_with_key(v, key)
    elif isinstance(data, list):
        for item in data:
            yield from find_dict_with_key(item, key)

print("PREAMBLES:")
for p in find_dict_with_key(data, 'preamble_text'):
    print(p)
print("SYSTEM PROMPTS:")
for p in find_dict_with_key(data, 'system_prompt'):
    print(p)

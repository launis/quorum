import json

with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    seed = json.load(f)

for i, block in enumerate(seed.get('prompt_blocks', [])):
    label = block.get('label', {})
    fi_label = label.get('translations', {}).get('fi', '')
    if not fi_label:
        fi_label = block.get('id', '')
    print(f"[{i}] {fi_label}")

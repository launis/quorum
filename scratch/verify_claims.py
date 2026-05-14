import json

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data['prompt_blocks']:
    if block.get('category_id') == 'matrix':
        for scale in block.get('scales', []):
            if len(scale.get('claims', [])) != 3:
                print(f"FAILED MECE: Block {block['id']} Scale {scale['score']} has {len(scale['claims'])} claims instead of 3.")
                exit(1)

print("MECE Check Passed: All matrix blocks have exactly 3 claims per scale.")

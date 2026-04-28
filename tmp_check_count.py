import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

matrix_blocks = [b for b in data['prompt_blocks'] if b.get('category_id') == 'matrix']
claims_blocks = [b for b in data['prompt_blocks'] if 'claims' in b.get('id', '') or 'matrix' in b.get('slug', '')]

print(f'Blocks with category_id=="matrix": {len(matrix_blocks)}')
for b in matrix_blocks:
    print(f"  - {b['slug']} ({b['id']})")

diff = [b for b in claims_blocks if b not in matrix_blocks]
print(f'\nBlocks with matrix in slug or claims in id but NOT category_id==matrix: {len(diff)}')
for b in diff:
    print(f"  - {b['slug']} ({b['id']}) - Category: {b.get('category_id')}")

import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Find all blocks that have 'claims' or 'matrix' in slug
blocks = [b for b in data['prompt_blocks'] if 'claims' in b or 'matrix' in b['slug']]
print(f'Total Matrix Blocks: {len(blocks)}')

profile = next((p for p in data['output_profiles'] if p['slug'] == 'holistic_audit'), None)
used_blocks = set()
for layout in profile['layouts']:
    for tb in layout.get('target_blocks', []):
        used_blocks.add(tb)

print(f'\nTotal matrices used in 3D layouts: {len(used_blocks)}')
print(used_blocks)

print('\nMatrices NOT used in 3D layouts:')
missing_matrices = []
for b in blocks:
    if b['id'] not in used_blocks and b.get('is_evaluative', True):
        en_title = b['title']['translations'].get('en', 'No EN Title') if isinstance(b.get('title'), dict) else b.get('slug')
        print(f"ID: {b['id']} | Slug: {b['slug']} | Title: {en_title}")
        missing_matrices.append(b['id'])

print('\nMissing matrix IDs list:')
print(missing_matrices)


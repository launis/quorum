import json

path = r'C:\src\quorum\data\db_v2.json'
with open(path, encoding='utf-8') as f:
    db = json.load(f)

for block in db.get('prompt_blocks', {}).values():
    if block.get('category_id') == 'matrix':
        scales = block.get('scales', [])
        for scale in scales:
            for claim in scale.get('claims', []):
                tdas = claim.get('tda_assertions', [])
                if tdas:
                    print(f"Block {block['id']} -> TDA ID: {tdas[0].get('tda_id')}")
        break

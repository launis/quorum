import json
with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for block in db.get('prompt_blocks', []):
    block_id = block.get('id')
    if block_id in ['blk_371c7724eeba40218409b5a3697ac1d3', 'blk_a0405e121dbf44bfa8ee80566f8d0c2a', 'blk_8b12be64227c4abd83e2f409b5c3ce28']:
        label_map = block.get('label', {}).get('translations', {})
        print(f'{block_id} ({label_map.get("en", "Unknown")}): allow_decimals={block.get("allow_decimals")}')

import json

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    high_ent = []
    for block in data.get('prompt_blocks', []):
        if block.get('type') == 'criteria' and 'criteria_schema' in block:
            for atom in block['criteria_schema']:
                if atom.get('high_entropy') is True:
                    high_ent.append((block['id'], atom))

    print(f"Found {len(high_ent)} high entropy rules.")
    for block_id, atom in high_ent:
        print(f"{block_id}: {atom['id']} - {atom['assertion']}")
except Exception as e:
    print(e)

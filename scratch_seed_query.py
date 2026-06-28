import json

with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    seed = json.load(f)

print(f"Total prompt blocks: {len(seed.get('prompt_blocks', []))}")
for i, block in enumerate(seed.get('prompt_blocks', [])):
    name = block.get('name', {}).get('fi', 'No Finnish Name')
    if name == 'No Finnish Name':
        name = block.get('name', {}).get('en', 'No English Name')
        
    instructions = block.get('instructions', '')
    if 'strategia' in name.lower() or 'päättely' in instructions.lower() or 'tiedolla' in name.lower() or 'epäsuora' in instructions.lower() or 'kulttuuri' in name.lower() or 'ilmapiiri' in name.lower() or 'sitoutuminen' in name.lower() or 'arvot' in name.lower() or 'valmius' in name.lower():
        print(f"[{i}] BLOCK: {name}")
        print(f"    INSTRUCTION: {instructions[:200]}...")
        print("-" * 50)
        

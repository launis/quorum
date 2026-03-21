import json

with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    d = json.load(f)

for s in d.get('steps', []):
    id = s.get('id')
    task = s.get('task_blueprint', '')
    blocks = s.get('prompt_blocks', [])
    
    if blocks:
        block_text = ', '.join(blocks)
    else:
        block_text = 'Ei matriiseja (Pelkkä teksti/synteesi)'
        
    print(f"- **{id}**\n  - Rooli: {task}\n  - Matriisit: {block_text}\n")

import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    d = json.load(f)

# Lookups
wf = next((w for w in d.get('workflows', []) if w['id'] == 'workflow_courtroom_20_full_audit'), None)
steps = {s['id']: s for s in d.get('steps', [])}
blocks = {b['id']: b['description']['translations'].get('fi', b['id']) for b in d.get('prompt_blocks', [])}

print("WORKFLOW EXECUTION PATH:")
for idx, s in enumerate(wf.get('steps', [])):
    bp_id = s.get('task_blueprint')
    bp = steps.get(bp_id, {})
    agent = bp.get('agent_id', 'unknown')
    prompts = bp.get('execution_config', {}).get('llm_prompts', [])
    
    print(f"\n{idx+1}. Node: {s['id']} | Blueprint: {bp_id} | Agent: {agent}")
    for p in prompts:
        desc = blocks.get(p, p).replace('\n', ' ')
        if len(desc) > 80: desc = desc[:80] + '...'
        print(f"   -> {p} | {desc}")


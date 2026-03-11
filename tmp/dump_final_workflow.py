import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    d = json.load(f)

# Find workflow
wf = next((w for w in d['workflows'] if w['id'] == 'workflow_courtroom_20_full_audit'), None)
if not wf:
    print("Workflow not found!")
    exit()

# Map blueprints to step configs
blueprint_to_step = {}
for s in d['steps']:
    blueprint_to_step[s['id']] = s

out_path = Path('c:/src/quorum/tmp/wf_layout.md')
with open(out_path, 'w', encoding='utf-8') as out:
    out.write("# Workflow 2.0 Full Audit: Step Verification\n\n")

    for wf_step in wf['steps']:
        bp_id = wf_step['task_blueprint']
        step_config = blueprint_to_step.get(bp_id, {})
        
        out.write(f"## Step: {wf_step['id']} (Blueprint: {bp_id})\n")
        
        deps = wf_step.get('depends_on', [])
        out.write(f"**Dependencies:** {deps}\n")
        
        input_mappings = wf_step.get('input_mappings', {})
        out.write(f"**Input Mappings:** {input_mappings}\n")
        
        prompts = step_config.get('prompt_blocks', [])
        out.write("**Prompts (in order):**\n")
        for idx, p in enumerate(prompts):
            out.write(f"  {idx + 1}. {p}\n")
            
        out.write("\n")

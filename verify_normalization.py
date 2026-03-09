import json
from pathlib import Path

def verify() -> None:
    data = json.loads(Path("backend_v2/seed/seed_data.json").read_text(encoding="utf-8"))
    blueprints = data.get("task_blueprints", [])
    workflows = data.get("workflows", [])
    
    print(f"Total TaskBlueprints: {len(blueprints)}")
    print(f"Total Workflows: {len(workflows)}")
    
    invalid_slugs = 0
    missing_blueprints = 0
    
    valid_blocks = {b["id"] for b in data.get("matrices", [])}
    valid_blueprints = {b["id"] for b in blueprints}

    for bp in blueprints:
        for block in bp.get("prompt_blocks", []):
             if "-" in block:
                 print(f"[Error: Blueprint {bp['id']}] Contains raw UUID block: {block}")
                 invalid_slugs += 1
             if block not in valid_blocks:
                 print(f"[Warning: Blueprint {bp['id']}] Block missing from matrices: {block}")

    for wf in workflows:
        print(f"WF: {wf['id']} -> step_count: {len(wf['steps'])}")
        for step in wf.get("steps", []):
            tb = step.get("task_blueprint")
            if tb and tb not in valid_blueprints:
                print(f"[Error: Workflow {wf['id']}] References non-existent blueprint: {tb}")
                missing_blueprints += 1
                
    if invalid_slugs == 0 and missing_blueprints == 0:
        print("\n✅ DATA ISO 100% NORMALIZED. No legacy UUIDs or orphaned blueprint assignments found.")
    else:
        print("\n❌ DATA NORMALIZATION FAILED!")

if __name__ == "__main__":
    verify()

import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def apply_mutations():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Map global steps (task_blueprints) to task_block_ids
    blueprint_to_blocks = {}
    for g_step in data.get("steps", []):
        bid = g_step.get("id")
        blocks = []
        for directive in g_step.get("scoring_directive", []):
            tb_id = directive.get("task_block_id")
            if tb_id:
                blocks.append(tb_id)
        blueprint_to_blocks[bid] = blocks

    mutated = False

    # 2. Iterate workflows
    for workflow in data.get("workflows", []):
        # Build local step mapping
        steprule_to_blocks = {}
        for node in workflow.get("steps", []):
            rule_id = node.get("id")
            bp_id = node.get("task_blueprint")
            steprule_to_blocks[rule_id] = blueprint_to_blocks.get(bp_id, [])

        # Process layouts
        profiles = workflow.get("output_profiles", {})
        for pid, profile in profiles.items():
            layouts = profile.get("layouts", [])
            for layout in layouts:
                # If target_blocks is missing or empty, build it from steps
                target_blocks = layout.get("target_blocks", [])
                if not target_blocks:
                    legacy_steps = layout.get("steps", [])
                    new_blocks = []
                    for ls in legacy_steps:
                        for b in steprule_to_blocks.get(ls, []):
                            if b not in new_blocks:
                                new_blocks.append(b)
                    
                    if new_blocks:
                        layout["target_blocks"] = new_blocks
                        mutated = True
                
                # Zero out legacy steps to finalize migration!
                if layout.get("steps"):
                    layout["steps"] = []
                    mutated = True

    if mutated:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("[MUTATOR] Successfully migrated all layouts to target_blocks and wiped legacy steps.")
    else:
        print("[MUTATOR] No targets required upgrading.")

if __name__ == "__main__":
    apply_mutations()

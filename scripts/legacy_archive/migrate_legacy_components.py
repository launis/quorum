import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

# Rename map: Old ID -> New ID
RENAME_MAP = {
    "method_1": "method_adversarial_simulation",
    "protocol_1": "protocol_logging",
    "method_3": "method_audit_questions",
    "protocol_3": "protocol_rfi",
    "protocol_4": "protocol_hitl",
    "requirement_1": "requirement_heterogeneity",
    "heuristic_1": "heuristic_temporal_audit",
    "heuristic_2": "heuristic_counterfactual_stress",
    "heuristic_3": "heuristic_abductive_challenge"
}

# Delete list: IDs to remove (because they are duplicates of new named components)
DELETE_LIST = [
    "rule_1", "rule_2", "rule_3", "rule_4", "rule_5", "rule_6", "rule_7", "rule_8", "rule_11", "rule_12", "rule_13", "rule_14", "rule_15",
    "mandate_1", "mandate_2", "mandate_3", "mandate_4",
    "HEADER_mandates", "HEADER_rules", "HEADER_methods", "HEADER_protocols", "HEADER_heuristics", "HEADER_principles", "HEADER_requirements"
]

def migrate_legacy():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data['components']
    steps = data['steps']
    
    # 1. Rename Components
    for comp in components:
        if comp['id'] in RENAME_MAP:
            old_id = comp['id']
            new_id = RENAME_MAP[old_id]
            comp['id'] = new_id
            print(f"Renamed component {old_id} -> {new_id}")

    # 2. Delete Components
    data['components'] = [c for c in components if c['id'] not in DELETE_LIST]
    print(f"Removed {len(components) - len(data['components'])} legacy components.")

    # 3. Update Steps Prompts
    for step in steps:
        prompts = step['execution_config']['llm_prompts']
        new_prompts = []
        for p in prompts:
            # Handle Renames
            if p in RENAME_MAP:
                new_prompts.append(RENAME_MAP[p])
            # Handle Deletes (skip them)
            elif p in DELETE_LIST:
                # Check if we need to replace deleted rule with new named rule?
                # The split_rules_and_mandates.py script ALREADY added the new named rules to the steps.
                # So we can safely drop the old numbered rules if they are in the list.
                # However, we must ensure we don't leave a gap if the new rule wasn't added.
                # But since we ran split_rules_and_mandates.py, the new rules SHOULD be there.
                print(f"  Dropping legacy ref {p} from {step['id']}")
                continue
            else:
                new_prompts.append(p)
        
        # Deduplicate
        seen = set()
        deduped_prompts = []
        for p in new_prompts:
            if p not in seen:
                deduped_prompts.append(p)
                seen.add(p)
        
        step['execution_config']['llm_prompts'] = deduped_prompts

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Migration complete.")

if __name__ == "__main__":
    migrate_legacy()

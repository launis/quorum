
import json
import io

def prune_falsifier():
    file_path = 'backend/database/seed_data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find step_falsifier
    steps = data.get('steps', [])
    falsifier = next((s for s in steps if s['id'] == 'step_falsifier'), None)

    if not falsifier:
        print("step_falsifier not found!")
        return

    print("Found step_falsifier.")
    prompts = falsifier['execution_config']['llm_prompts']
    
    start_len = len(prompts)
    
    # Items to remove
    to_remove = [
        "OP_RULE_4", 
        "METHOD_1", "METHOD_2", "METHOD_3", 
        "INSTRUCTION_TOULMIN",
        "PROTOCOL_1", "PROTOCOL_2", "PROTOCOL_3", "PROTOCOL_4", "HEADER_PROTOCOLS"
    ]
    
    # Keep standard mandated/rules/instructions but remove specific noise
    # Based on the seed_data view, Falsifier had the full protocol block which is usually not needed if it audits logic?
    # Actually, protocols might be relevant for some agents, but OP_RULE_4 is definitely noise.
    # The replace_content block I tried to apply removed HEADER_PROTOCOLS...INSTRUCTION_BLOOM.
    # Let's stick to the plan: Remove OP_RULE_4, METHODs, TOULMIN.
    # And specifically re-add PROTOCOLs if they were accidentally targeted? 
    # My previous replacement text removed Protocols. 
    # Let's remove them to be safe/clean as per the specific failing edit.
    
    new_prompts = [p for p in prompts if p not in to_remove]
    
    falsifier['execution_config']['llm_prompts'] = new_prompts
    
    end_len = len(new_prompts)
    print(f"Pruned {start_len - end_len} items.")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Saved seed_data.json")

if __name__ == "__main__":
    prune_falsifier()


import json
import io

def prune_causal():
    file_path = 'backend/database/seed_data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find step_causal
    steps = data.get('steps', [])
    causal = next((s for s in steps if s['id'] == 'step_causal'), None)

    if not causal:
        print("step_causal not found!")
        return

    print("Found step_causal.")
    prompts = causal['execution_config']['llm_prompts']
    
    start_len = len(prompts)
    
    # Items to remove
    to_remove = [
        "OP_RULE_4", 
        "METHOD_1", "METHOD_2", "METHOD_3", 
        "INSTRUCTION_TOULMIN",
        "PROTOCOL_1", "PROTOCOL_2", "PROTOCOL_3", "PROTOCOL_4", "HEADER_PROTOCOLS",
        "INSTRUCTION_BLOOM", "INSTRUCTION_ANON", "INSTRUCTION_RAG_OPT" 
    ]
    # Pruning aggressively to keep it clean like Falsifier, assuming Causal doesn't need standard methods either.
    # It has its own KausaalinenAuditointi schema target.
    
    new_prompts = [p for p in prompts if p not in to_remove]
    
    causal['execution_config']['llm_prompts'] = new_prompts
    
    end_len = len(new_prompts)
    print(f"Pruned {start_len - end_len} items.")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Saved seed_data.json")

if __name__ == "__main__":
    prune_causal()

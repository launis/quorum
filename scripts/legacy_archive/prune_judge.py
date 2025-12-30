
import json

def prune_judge_and_panel():
    file_path = 'backend/database/seed_data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    steps = data.get('steps', [])
    
    # 1. Prune Judge
    judge = next((s for s in steps if s['id'] == 'step_judge'), None)
    if judge:
        print("Found step_judge.")
        prompts = judge['execution_config']['llm_prompts']
        to_remove = [
            "OP_RULE_4", 
            "METHOD_1", "METHOD_2", "METHOD_3", 
            "INSTRUCTION_TOULMIN",
            "PROTOCOL_1", "PROTOCOL_2", "PROTOCOL_3", "PROTOCOL_4", "HEADER_PROTOCOLS",
            "INSTRUCTION_BLOOM", "INSTRUCTION_ANON", "INSTRUCTION_RAG_OPT"
        ]
        # Keep TASK_JUDGE, MANDATES, RULES.
        new_prompts = [p for p in prompts if p not in to_remove]
        judge['execution_config']['llm_prompts'] = new_prompts
        print(f"Pruned {len(prompts) - len(new_prompts)} items from Judge.")

    # 2. Prune Panel
    # Wait, in the user's file view, I saw 'step_archivist'. where is 'step_panel'? 
    # Let's find it. 
    panel = next((s for s in steps if s['component'] == 'PanelAgent'), None)
    if panel:
         print(f"Found PanelAgent (id: {panel['id']}).")
         prompts = panel['execution_config']['llm_prompts']
         to_remove = [
            "OP_RULE_4", 
            "METHOD_1", "METHOD_2", "METHOD_3", 
            "INSTRUCTION_TOULMIN",
            "PROTOCOL_1", "PROTOCOL_2", "PROTOCOL_3", "PROTOCOL_4", "HEADER_PROTOCOLS",
            "INSTRUCTION_BLOOM", "INSTRUCTION_ANON", "INSTRUCTION_RAG_OPT"
        ]
         new_prompts = [p for p in prompts if p not in to_remove]
         panel['execution_config']['llm_prompts'] = new_prompts
         print(f"Pruned {len(prompts) - len(new_prompts)} items from Panel.")
    else:
        print("PanelAgent not found.")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Saved seed_data.json")

if __name__ == "__main__":
    prune_judge_and_panel()

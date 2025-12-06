
import json
import os

SEED_PATH = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def update_seed_data():
    if not os.path.exists(SEED_PATH):
        print(f"Error: {SEED_PATH} not found.")
        return

    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    # Update Steps
    if "steps" in data:
        for step in data["steps"]:
            exec_config = step.get("execution_config", {})
            prompts = exec_config.get("llm_prompts", [])
            
            # Avoid duplicates
            if "CONTEXT_NOW" not in prompts:
                prompts.insert(0, "CONTEXT_NOW")
                exec_config["llm_prompts"] = prompts
                updated_count += 1
                print(f"Updated step: {step.get('id')}")

    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully updated {updated_count} steps in seed_data.json")

if __name__ == "__main__":
    update_seed_data()

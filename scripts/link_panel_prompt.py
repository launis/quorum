
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/db.json")
SEED_FILE = os.path.join(os.path.dirname(__file__), "../backend/seed/seed_data.json")

def update_panel_config(file_path):
    print(f"Reading {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    workflows_container = data.get("workflows")
    
    # Normalize to list of workflow objects
    workflows_list = []
    if isinstance(workflows_container, dict):
        workflows_list = list(workflows_container.values())
    elif isinstance(workflows_container, list):
        workflows_list = workflows_container
    else:
        print(f"Warning: 'workflows' key not found or invalid type in {file_path}")
        return

    updated_count = 0
    for wf in workflows_list:
        steps = wf.get("steps", [])
        for step in steps:
            if step.get("id") == "step_panel":
                config = step.get("config", {})
                prompts = config.get("llm_prompts", [])
                
                if "PANEL_PROMPT_TEMPLATE" not in prompts:
                    print(f"Updating step_panel in workflow '{wf.get('id')}'...")
                    prompts.append("PANEL_PROMPT_TEMPLATE")
                    config["llm_prompts"] = prompts
                    step["config"] = config
                    updated_count += 1
                else:
                    print(f"step_panel in workflow '{wf.get('id')}' already has prompt template.")

    if updated_count > 0:
        print(f"Writing updated data to {file_path}...")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Success.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    update_panel_config(DB_FILE)
    update_panel_config(SEED_FILE)

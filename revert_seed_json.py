import json

FILE_PATH = 'backend/seed/seed_data.json'

def revert_seed_json():
    try:
        with open(FILE_PATH, encoding='utf-8') as f:
            data = json.load(f)

        workflows = data.get('workflows', [])
        count = 0

        for wf in workflows:
            steps = wf.get("steps", [])
            for step in steps:
                # If step has config AND task_key, it might be a duplicate if config is standard.
                # User wants "define once". So we remove 'config' from workflow steps
                # IF the global step definition exists and has it (safe assumption per user instruction).
                # Actually, user said: "step:it ja niiden configuraatio esitellään vain kerran"
                # So we should strip 'config' from ALL workflow steps that are just references.

                # Exception: Overrides?
                # If the workflow step config is different?
                # For now, I will strip all 'llm_prompts' from config.
                # If config has other things (like model_strategy override), maybe keep?
                # But my previous fix added 'llm_prompts' and 'model_strategy'.

                if 'config' in step:
                    # Remove 'llm_prompts' specifically
                    if 'llm_prompts' in step['config']:
                        del step['config']['llm_prompts']
                        count += 1

                    # If config is now empty or just has 'model_strategy', maybe we can leave it?
                    # Or remove 'config' entirely if empty?
                    if not step['config']:
                        del step['config']
                    # Use 'model_strategy' from global too?
                    # The global steps I saw earlier had 'model_strategy'.
                    # So I should remove 'config' entirely if it matches global?
                    # Let's start by removing 'llm_prompts'.

        print(f"Removed 'llm_prompts' from {count} steps.")

        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error: {e}")

revert_seed_json()

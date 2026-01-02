
import json
import os

SEED_PATH = r"backend/database/seed_data.json"

def apply_modernization():
    print(f"Reading {SEED_PATH}...")
    try:
        with open(SEED_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("UTF-8 read failed, trying UTF-16")
        with open(SEED_PATH, 'r', encoding='utf-16') as f:
            data = json.load(f)

    # 1. Update Steps (max_tokens)
    target_steps = ['step_guard', 'step_analyst', 'step_judge']
    count_steps = 0
    if "steps" in data:
        for step in data['steps']:
            if step['id'] in target_steps:
                if 'llm_config' not in step:
                    step['llm_config'] = {}
                step['llm_config']['max_tokens'] = 8192
                count_steps += 1
                print(f"Updated max_tokens for {step['id']}")
    print(f"Updated {count_steps} steps.")

    # 2. Update Tasks (OUTPUT_CONSTRAINT)
    count_tasks = 0
    constraint = "\n\nOUTPUT_CONSTRAINT: Do NOT repeat the input text. Output concise JSON only."
    if "components" in data:
        for comp in data['components']:
            if comp.get('id', '').startswith("TASK_"):
                # Avoid double append if run multiple times
                if constraint.strip() not in comp.get('content', ''):
                    comp['content'] = comp.get('content', '') + constraint
                    count_tasks += 1
    print(f"Updated {count_tasks} task prompts.")

    # 3. Rename default_model_id -> model_name in system_config
    # system_config -> [ {models: { google: { fast: { ... } } } } ]
    count_renames = 0
    if "system_config" in data:
        for item in data['system_config']:
            if item.get('type') == 'model_registry':
                models = item.get('models', {})
                for provider, variants in models.items():
                    for variant, config in variants.items():
                        if "default_model_id" in config:
                            config["model_name"] = config.pop("default_model_id")
                            count_renames += 1
    print(f"Renamed {count_renames} model keys.")

    # Save
    print("Saving seed_data.json (UTF-8)...")
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Modernization applied.")

if __name__ == "__main__":
    apply_modernization()

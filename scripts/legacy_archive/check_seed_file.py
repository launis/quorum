import json

def check():
    with open('backend/database/seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    steps = data.get('steps', [])
    guard = next((s for s in steps if s['id'] == 'step_guard'), None)
    
    if not guard:
        print("step_guard not found in seed_data.json")
        return
        
    prompts = guard['execution_config']['llm_prompts']
    print(f"step_guard prompts in seed_data.json: {prompts}")
    
    required = ['HEADER_MANDATES', 'TASK_GUARD']
    missing = [r for r in required if r not in prompts]
    if missing:
        print(f"MISSING in file: {missing}")
    else:
        print("seed_data.json looks CORRECT.")

if __name__ == "__main__":
    check()

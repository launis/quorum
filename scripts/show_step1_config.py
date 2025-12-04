import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def show_step1_config():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find step_1
    step1 = next((s for s in data['steps'] if s['id'] == 'step_1'), None)
    if not step1:
        print("Step 1 not found!")
        return

    print(f"--- VAIHE 1: {step1['name']} ---")
    print(f"Kuvaus: {step1['description']}\n")
    
    prompts = step1['execution_config']['llm_prompts']
    print("Suunnitellut komponentit (LLM Prompts):")
    
    components = {c['id']: c for c in data['components']}
    
    for prompt_id in prompts:
        comp = components.get(prompt_id)
        if comp:
            print(f"\n[{comp['type'].upper()}] {comp['name']} (ID: {prompt_id})")
            # Print first 200 chars of content
            content = comp.get('content', 'No content')
            print(f"Sisältö: {content[:200]}..." if len(content) > 200 else f"Sisältö: {content}")
        else:
            print(f"\n[MISSING] ID: {prompt_id}")

if __name__ == "__main__":
    show_step1_config()

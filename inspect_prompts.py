import json

with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== STEPS ===")
for step in data.get('steps', []):
    name = step.get('name', '')
    if name in ['Interaction Analyst', 'Profiler', 'Panel', 'Judge', 'XAI Reporter']:
        print(f"Step: {name}")
        print(f"  Inputs: {step.get('inputs')}")
        
print("\n=== PROMPTS ===")
for prompt in data.get('llm_prompts', []):
    name = prompt.get('name', '')
    if 'Interaction' in name or 'Profiler' in name or 'Panel' in name or 'Judge' in name or 'XAI' in name:
        text = prompt.get('text', '')
        print(f"Prompt Name: '{name}' | ID: {prompt.get('id')}")
        if '{{' in text:
            print(f"  Has template vars: {[word for word in text.split() if '{{' in word]}")
        if 'average' in text.lower() or 'calculate' in text.lower() or 'total' in text.lower() or 'normalize' in text.lower():
            print("  Contains math/average/normalize directives.")

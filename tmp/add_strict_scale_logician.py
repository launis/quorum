import json
from pathlib import Path

def enforce_strict_scale():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    block_id = "block_instructionstrictscale"

    for step in data.get('steps', []):
        if step['id'] == 'step_logician':
            if 'prompt_blocks' not in step:
                step['prompt_blocks'] = []
            
            if block_id not in step['prompt_blocks']:
                # The prompt blocks should ideally have matrix_logician at the end.
                # Just appending to the list is fine, since other rules are already there.
                step['prompt_blocks'].append(block_id)
            print(f"Updated step {step['id']} prompts: {step['prompt_blocks']}")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Strict scale enforced for Logician.")

if __name__ == "__main__":
    enforce_strict_scale()

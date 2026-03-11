import json
from pathlib import Path
from uuid import uuid4

def inject_strictness_block():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Create the new Prompt Block
    strictness_block = {
        "id": "block_instruction_strictness",
        "slug": "block_instruction_strictness",
        "category": "instruction",
        "description": {
            "translations": {
                "fi": "HUOMIO AUDITOINNIN KRIITTISYYS: Käyttäjä on asettanut tämän analyysin tiukkuustasoksi {{ inputs.strictness_level|default(50) }} / 100. Jos arvo on yli 80: Ole armoton, etsi pienimmätkin loogiset ja rakenteelliset virheet. Vaadi täydellisyyttä vahvimmalla arvosanalla hylkäykselle. Jos arvo on alle 40: Ole rakentava ja sallivampi. Huomioi enemmän hyvää tarkoitusta, ja liputa vain aidosti vaaralliset tai täysin puuttuvat rakenteet. Arvolla 40-80 tee täysin objektiivinen normaalianalyysi. Sisäistä tämä ja muuta subjektiivista analyytikon tai tuomarin tulkintaasi (1.0-5.0) tiukasti tämän vaatimustason mukaiseksi.",
                "en": "ATTENTION AUDIT STRICTNESS: The user has set the strictness level for this analysis to {{ inputs.strictness_level|default(50) }} / 100. If the value is over 80: Be merciless, find the smallest logical and structural errors. Demand perfection with the strongest penalty score. If the value is under 40: Be constructive and more lenient. Acknowledge good intent, and only flag genuinely dangerous or completely missing structures. At 40-80, perform a fully objective standard analysis. Internalize this and bias your subjective analyst or judge scoring (1.0-5.0) strictly according to this requirement level."
            }
        }
    }

    # Ensure it's not already there
    existing_blocks = [b['id'] for b in data.get('prompt_blocks', [])]
    if 'block_instruction_strictness' not in existing_blocks:
        data['prompt_blocks'].append(strictness_block)
        print("Inserted new block: block_instruction_strictness")
    else:
        # Update it just in case
        for pb in data['prompt_blocks']:
            if pb['id'] == 'block_instruction_strictness':
                pb['description'] = strictness_block['description']
                print("Updated existing block: block_instruction_strictness")

    # 2. Inject it into Target Steps
    # We want it to be placed right after context/rules, but before the "Task" block
    # Best place is typically right before the `matrix_` block so the identity inherits the strictness.
    target_steps = [
        'step_analyst',
        'step_logician',
        'step_falsifier',
        'step_causal_analyst',
        'step_performativity_detector',
        'step_judge',
        'step_overseer' # Ethical strictness
    ]

    for step in data.get('steps', []):
        if step['id'] in target_steps:
            prompts = step.get('prompt_blocks', [])
            if 'block_instruction_strictness' not in prompts:
                # Find the matrix block to insert before it
                matrix_idx = next((i for i, p in enumerate(prompts) if p.startswith('matrix_')), len(prompts) - 1)
                
                # Insert
                prompts.insert(matrix_idx, 'block_instruction_strictness')
                step['prompt_blocks'] = prompts
                print(f"Injected strictness block into {step['id']}")

    # Keep default scales for Judge (1.0-5.0) to not break UI yet. 
    # Scaling will happen in specific endpoint/router logically as planned.

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Strictness implementation successfully written to seed_data.json.")

if __name__ == "__main__":
    inject_strictness_block()

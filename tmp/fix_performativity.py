import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    data = json.load(f)

new_block_id = "block_taskperformativity"
new_block = {
  "id": new_block_id,
  "label": {
    "default_locale": "fi",
    "translations": {
      "fi": "TASK_PERFORMATIVITY"
    }
  },
  "description": {
    "default_locale": "fi",
    "translations": {
      "fi": """ROOLI: Performatiivisuuden Tunnistaja (Illusion of Control Audit)

TEHTÄVÄT:

* ETSI 'Väsyneitä Komentoja' (esim. 'jatka', 'lisää').
* TUNNISTA 'Illusion of Control': Käyttäjä luulee ohjaavansa, mutta AI tekee aloitteet.
* LIPUTA 'Performatiivinen', jos käyttäjän aito panos on minimaalinen mutta itsearviointi mahtipontinen.
* SOVELLA Goodhartin lakia: Etsi 'Epäilyttävää Täydellisyyttä' (Suspicious Perfection).

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN seuraavan JSON-skeeman mukaisesti (PerformativityOutput).
VAROITUS: ÄLÄ LITISTÄ (FLATTEN) RAKENNETTA. Sinun on palautettava 'performativity_analysis' -objekti, jonka SISÄLLÄ ovat analyysikentät.
Varmista, että vastaus sisältää 'reasoning_trace' -merkkijonon ja 'performativity_analysis' -objektin:
{{SCHEMA_EXAMPLE}}"""
    }
  },
  "category_id": "system_rule",
  "type": "instruction",
  "allow_decimals": False,
  "strictness_level": 50,
  "require_justification": False
}

found = False
for i, pb in enumerate(data.get('prompt_blocks', [])):
    if pb['id'] == new_block_id:
        data['prompt_blocks'][i] = new_block
        found = True
        break

if not found:
    data['prompt_blocks'].append(new_block)

for step in data.get('steps', []):
    if step['id'] == 'step_performativity_detector':
        if 'prompt_blocks' not in step:
            step['prompt_blocks'] = []
            
        if new_block_id not in step['prompt_blocks']:
            try:
                idx = step['prompt_blocks'].index('matrix_goodhart')
                step['prompt_blocks'].insert(idx, new_block_id)
            except ValueError:
                step['prompt_blocks'].append(new_block_id)
        
        print(f"Updated step {step['id']} prompts: {step['prompt_blocks']}")

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Done writing to seed_data.json")

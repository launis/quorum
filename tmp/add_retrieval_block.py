import json
from pathlib import Path

def add_retrieval_block():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    new_block_id = "block_taskretrieval"
    new_block = {
      "id": new_block_id,
      "label": {
        "default_locale": "fi",
        "translations": {
          "fi": "TASK_RETRIEVAL"
        }
      },
      "description": {
        "default_locale": "fi",
        "translations": {
          "fi": "ROOLI: TIEDONHAKU-AGENTTI (Retrieval Agent)\n\nTEHTÄVÄT:\n\n* Hae annetusta aineistosta olennaiset faktat vastaamaan käyttäjän syötteisiin tai järjestelmän tarpeisiin.\n* Jäsennä faktat rakenteellisesti myöhempien agenttien analyysiä varten.\n\nKÄSKE: Tulosta vastauksesi TÄSMÄLLEEN seuraavan JSON-skeeman mukaisesti (RetrievalOutput).\nVAROITUS: ÄLÄ LITISTÄ (FLATTEN) RAKENNETTA.\nVarmista, että vastaus sisältää 'reasoning_trace' -merkkijonon ja 'retrieved_facts' -listan:\n{{SCHEMA_EXAMPLE}}"
        }
      },
      "category_id": "system_rule",
      "type": "instruction",
      "allow_decimals": False,
      "strictness_level": 50,
      "require_justification": False
    }

    # Add block if missing
    found = False
    for i, pb in enumerate(data.get('prompt_blocks', [])):
        if pb['id'] == new_block_id:
            data['prompt_blocks'][i] = new_block
            found = True
            break
    if not found:
        data['prompt_blocks'].append(new_block)

    # Attach to step_retrieval_agent
    for step in data.get('steps', []):
        if step['id'] == 'step_retrieval_agent':
            if 'prompt_blocks' not in step:
                step['prompt_blocks'] = []
            if new_block_id not in step['prompt_blocks']:
                step['prompt_blocks'].append(new_block_id)
            print(f"Updated step {step['id']} prompts: {step['prompt_blocks']}")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Retrieval block added successfully.")

if __name__ == "__main__":
    add_retrieval_block()

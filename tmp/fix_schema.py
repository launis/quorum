import json
from pathlib import Path

def fix_strictness_schema():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    strictness_block = {
        "id": "block_instruction_strictness",
        "slug": "block_instruction_strictness",
        "category_id": "instruction",
        "type": "string",
        "strictness_level": 50,
        "require_justification": False,
        "label": {
            "default_locale": "fi",
            "translations": {
                "fi": "Tiukkuustason asetukset",
                "en": "Strictness Settings"
            }
        },
        "description": {
            "default_locale": "fi",
            "translations": {
                "fi": "HUOMIO AUDITOINNIN KRIITTISYYS: Käyttäjä on asettanut tämän analyysin tiukkuustasoksi {{ inputs.strictness_level|default(50) }} / 100. Jos arvo on yli 80: Ole armoton, etsi pienimmätkin loogiset ja rakenteelliset virheet. Vaadi täydellisyyttä vahvimmalla arvosanalla hylkäykselle. Jos arvo on alle 40: Ole rakentava ja sallivampi. Huomioi enemmän hyvää tarkoitusta, ja liputa vain aidosti vaaralliset tai täysin puuttuvat rakenteet. Arvolla 40-80 tee täysin objektiivinen normaalianalyysi. Sisäistä tämä ja muuta subjektiivista analyytikon tai tuomarin tulkintaasi (1.0-5.0) tiukasti tämän vaatimustason mukaiseksi.",
                "en": "ATTENTION AUDIT STRICTNESS: The user has set the strictness level for this analysis to {{ inputs.strictness_level|default(50) }} / 100. If the value is over 80: Be merciless, find the smallest logical and structural errors. Demand perfection with the strongest penalty score. If the value is under 40: Be constructive and more lenient. Acknowledge good intent, and only flag genuinely dangerous or completely missing structures. At 40-80, perform a fully objective standard analysis. Internalize this and bias your subjective analyst or judge scoring (1.0-5.0) strictly according to this requirement level."
            }
        }
    }

    found = False
    for pb in data.get('prompt_blocks', []):
        if pb['id'] == 'block_instruction_strictness':
            pb.clear()
            pb.update(strictness_block)
            found = True
            break
            
    if not found:
        data['prompt_blocks'].append(strictness_block)

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Fixed prompt block schema.")

if __name__ == "__main__":
    fix_strictness_schema()

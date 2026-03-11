import json
from pathlib import Path

def apply_philosophical_fixes():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Fix Performativity Paradox (Authenticity Score Inversion)
    for pb in data.get('prompt_blocks', []):
        if pb['id'] == 'block_taskperformativity':
            desc = pb.get('description', {}).get('translations', {}).get('fi', '')
            if 'authenticity_score' in desc and '3.0 on KORKEIN' not in desc:
                new_instruction = (
                    " HUOMIO MATEMATIIKKA (Authenticity Score): "
                    "Arvo 3.0 on KORKEIN ja PARAS (Organic/Aito). "
                    "Arvo 2.0 on KESKITASO (Performative/Teatteria). "
                    "Arvo 1.0 on ALIN (Manipulative). "
                    "Järjestelmä laskee keskiarvoja: mitä enemmän performatiivisuutta löydät, sitä PIENEMPI numeron (1.0-2.0) tulee olla!"
                )
                pb['description']['translations']['fi'] = desc.replace(
                    "Vaaditaan 1-desimaalin tarkkuus (esim. 2.5).", 
                    f"Vaaditaan 1-desimaalin tarkkuus (esim. 2.5).{new_instruction}"
                )
                print("Applied philosophical fix to block_taskperformativity")

        # 2. Fix XAI Reporter Synthesis vs Aggregation
        if pb['id'] == 'block_taskxai':
            desc = pb.get('description', {}).get('translations', {}).get('fi', '')
            if 'SYNTEESI, EI LISTAUS' not in desc:
                suggestion = (
                    " SYNTEESI, EI LISTAUS: "
                    "Älä toista mekaanisesti mitä muut agentit sanoivat. "
                    "Käytä Hegelin dialektiikkaa: muodosta synteesi siitä, MIKSI ja MITEN "
                    "asiayhteydet, vinoumat ja faktat johtivat Tuomarin antamaan arvosanaan. "
                    "Paljasta piilevät syy-seuraussuhteet (""Why""), älä vain luettele (""What"")."
                )
                
                pb['description']['translations']['fi'] = desc + suggestion
                print("Applied Hegelian synthesis instruction to block_taskxai")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    apply_philosophical_fixes()

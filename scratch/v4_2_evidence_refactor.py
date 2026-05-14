import json
import re
import os

SEED_FILE = "backend_v2/seed/seed_data.json"

def apply_evidence_driven_doctrine(text):
    if 'ACCEPT' not in text.upper() and 'REJECT' not in text.upper():
        return text

    # 1. Pelastetaan semanttinen ehto "If X -> ACCEPT" ja muutetaan se poimintavaatimukseksi
    text = re.sub(
        r'(?i)If\s+(.*?)\s*->\s*ACCEPT[^\.]*\.?', 
        r'EXTRACTION CONDITION: \1.', 
        text
    )
    
    # 2. Käsitellään negatiiviset rajoitteet (Vice rules)
    text = re.sub(
        r'(?i)If\s+(.*?)\s*->\s*REJECT[^\.]*\.?', 
        r'NEGATIVE CONDITION (RETURN NULL IF MET): \1.', 
        text
    )
    
    # 3. Siivotaan jäljelle jääneet orvot rakenteet
    text = re.sub(r'(?i)Otherwise\s*->\s*REJECT[^\.]*\.?', '', text)
    text = re.sub(r'(?i)->\s*ACCEPT[^\.]*\.?', '', text)
    text = re.sub(r'(?i)->\s*REJECT[^\.]*\.?', '', text)
    text = re.sub(r'(?i)ENFORCEMENT RULE:.*', '', text).strip()
    
    if "BANNED CONCEPTS:" in text and "subjective interpretation" not in text.lower():
        text = text.replace("BANNED CONCEPTS:", "BANNED CONCEPTS: Do NOT evaluate intent or excuse missing context. ")
        
    # 4. Uusi Mandaatti 3 (Forensic Investigator) - HUOM: Kielimuurin ylittävä joustavuus
    mechanical_enforcement = (
        " ENFORCEMENT MANDATE: You are a strict extraction engine, not a judge. "
        "Step 1: Locate potential text using Lexical Anchors as semantic hints (allow exact translations in the target language). "
        "Step 2: Read the bounding box. IF AND ONLY IF the EXTRACTION CONDITION is physically demonstrated in the text, EXTRACT THE EXACT QUOTE. "
        "Step 3: IF THE CONDITION IS NOT EXPLICITLY MET, OR IF A NEGATIVE CONDITION IS MET, RETURN NULL. DO NOT RATIONALIZE OR EXPLAIN AWAY FAILURES."
    )
    
    clean_text = re.sub(r'\s+', ' ', text + mechanical_enforcement).strip()
    return clean_text

def refactor_seed_data():
    if not os.path.exists(SEED_FILE):
        print(f"❌ VIRHE: Tiedostoa {SEED_FILE} ei löydy. Varmista, että olet projektin juuressa.")
        return

    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    protected_ai_descriptions = 0

    for block in data.get('prompt_blocks', []):
        if block.get('category_id') == 'matrix' and 'scales' in block:
            for scale in block['scales']:
                for claim in scale.get('claims', []):
                    if "ai_description" in claim:
                        protected_ai_descriptions += 1
                        
                    for tda in claim.get('tda_assertions', []):
                        old_desc = tda.get('ai_rule_description', '')
                        
                        if "ACCEPT" in old_desc.upper() or "REJECT" in old_desc.upper():
                            new_desc = apply_evidence_driven_doctrine(old_desc)
                            if new_desc != old_desc:
                                tda['ai_rule_description'] = new_desc
                                updated_count += 1

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ V4.2 Evidence-Driven Extraction -siivous suoritettu!")
    print(f"✅ Päivitetty {updated_count} TDA-sääntöä Rikostutkija-formaattiin.")
    print(f"✅ Sääntö 22 varmistettu: {protected_ai_descriptions} ai_description -kenttää suojeltu Pydantic-kaatumisten estämiseksi.")

if __name__ == "__main__":
    refactor_seed_data()

import json
import re
import os

SEED_FILE = "backend_v2/seed/seed_data.json"

def apply_zero_interpretation_doctrine(text):
    """
    Tuhoaa kognitiiviset booleanit (ACCEPT/REJECT) ja korvaa ne 
    mekaanisella poimintakäskyllä.
    """
    if 'ACCEPT' not in text.upper() and 'REJECT' not in text.upper():
        return text

    # 1. Poistetaan vanha kognitiivinen ACCEPT/REJECT -logiikka lausekkeineen
    text = re.sub(r'(?i)If.*?->\s*ACCEPT[^\.]*\.', '', text)
    text = re.sub(r'(?i)Otherwise\s*->\s*REJECT[^\.]*\.', '', text)
    text = re.sub(r'(?i)->\s*ACCEPT[^\.]*\.', '', text)
    text = re.sub(r'(?i)->\s*REJECT[^\.]*\.', '', text)
    text = re.sub(r'(?i)ACCEPT\s*\(.*?\)', '', text)
    text = re.sub(r'(?i)REJECT\s*\(.*?\)', '', text)
    
    # 2. Poistetaan vanha Enforcement Rule
    text = re.sub(r'(?i)ENFORCEMENT RULE:.*?(?=\.|$)', '', text).strip()
    
    # 3. Varmistetaan, että BANNED CONCEPTS kieltää subjektiivisuuden ekspliittisesti
    if "BANNED CONCEPTS:" in text and "subjective interpretation" not in text.lower():
        text = text.replace("BANNED CONCEPTS:", "BANNED CONCEPTS: Do NOT evaluate intent or use subjective interpretation. ")
    
    # 4. Lisätään V4.1 Zero-Interpretation -mandaatti (Mekaaninen poiminta)
    mechanical_enforcement = (
        " ENFORCEMENT RULE (Mechanical Extraction): DO NOT evaluate if the rule is 'satisfied' or 'broken'. "
        "Document the mechanical presence of lexical anchors in reasoning_trace. "
        "EXTRACT EXACT QUOTE IF AND ONLY IF THE EXACT LEXICAL ANCHORS ARE PRESENT IN THE DESCRIBED CONTEXT. "
        "IF MISSING, RETURN NULL."
    )
    
    # Siistitään ylimääräiset välilyönnit
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

    # Iteroidaan prompt_blocks läpi
    for block in data.get('prompt_blocks', []):
        if block.get('category_id') == 'matrix' and 'scales' in block:
            for scale in block['scales']:
                for claim in scale.get('claims', []):
                    # Varmistetaan Sääntö 22: Pydanticin vaatiman ai_descriptionin suojelu
                    if "ai_description" in claim:
                        protected_ai_descriptions += 1
                        
                    for tda in claim.get('tda_assertions', []):
                        old_desc = tda.get('ai_rule_description', '')
                        
                        if "ACCEPT" in old_desc.upper() or "REJECT" in old_desc.upper():
                            new_desc = apply_zero_interpretation_doctrine(old_desc)
                            if new_desc != old_desc:
                                tda['ai_rule_description'] = new_desc
                                updated_count += 1

    # Tallennetaan päivitetty JSON takaisin
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Kognitiivinen siivous (V4.1) suoritettu!")
    print(f"✅ Päivitetty {updated_count} TDA-sääntöä mekaanisiksi ja deterministisiksi.")
    print(f"✅ Sääntö 22 varmistettu: {protected_ai_descriptions} ai_description -kenttää suojeltu Pydantic-kaatumisten estämiseksi.")

if __name__ == "__main__":
    refactor_seed_data()

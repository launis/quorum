import json
import re
import os

SEED_FILE = "backend_v2/seed/seed_data.json"

def apply_evidence_driven_doctrine(text):
    if 'ACCEPT' not in text.upper() and 'REJECT' not in text.upper():
        return text

    # 1. Standardisoi trace-terminologia
    text = text.replace("reasoning_trace", "`mechanical_trace`")

    # 2. Konvertoidaan ACCEPT / REJECT mekaanisiksi ehdoiksi
    text = re.sub(r'(?i)If\s+(.*?)\s*->\s*ACCEPT[^\.]*\.?', r'EXTRACTION CONDITION: \1.', text)
    text = re.sub(r'(?i)If\s+(.*?)\s*->\s*REJECT[^\.]*\.?', r'NEGATIVE CONDITION (RETURN NULL IF MET): \1.', text)
    
    # 3. Siivotaan orvot nuolet
    text = re.sub(r'(?i)Otherwise\s*->\s*REJECT[^\.]*\.?', '', text)
    text = re.sub(r'(?i)->\s*ACCEPT[^\.]*\.?', '', text)
    text = re.sub(r'(?i)->\s*REJECT[^\.]*\.?', '', text)
    
    # 4. Pelastetaan kognitiivinen kitka ja siistitään se toisteisuudesta
    def clean_enforcement(match):
        content = match.group(1).strip()
        # Poistetaan "before extracting exact_quote" yms. kohina
        content = re.sub(r'(?i)\s*before\s+extracting.*', '.', content)
        content = re.sub(r'(?i)\s*first\.?', '.', content)
        return f"TRACE REQUIREMENT: {content}"
        
    text = re.sub(r'(?i)ENFORCEMENT RULE:\s*(.*)', clean_enforcement, text)
    
    # 5. Estetään intentioiden arvailu
    if "BANNED CONCEPTS:" in text and "intent" not in text.lower():
        text = text.replace("BANNED CONCEPTS:", "BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. ")
        
    # 6. UUSI V4.3 MANDAATTI (Blind Extraction & Strict Fit)
    mechanical_enforcement = (
        " ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. "
        "Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. "
        "Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. "
        "STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. "
        "Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES."
    )
    
    clean_text = re.sub(r'\s+', ' ', text + mechanical_enforcement).strip()
    clean_text = clean_text.replace("..", ".").replace(" .", ".") 
    return clean_text

def patch_system_directives(data):
    """Päivittää ylätason system_directive -promptit tukemaan uutta roolia."""
    for block in data.get('prompt_blocks', []):
        if 'ai_description' in block and '<system_directive>' in block['ai_description']:
            desc = block['ai_description']
            # Korvataan Evaluate -> Extract
            desc = re.sub(
                r'<rule>Strict Boolean Logic:.*?</rule>', 
                '<rule>Forensic Extraction: Do not act as a judge. Your sole objective is to extract verbatim quotes matching the conditions. Return JSON null otherwise.</rule>', 
                desc, flags=re.DOTALL | re.IGNORECASE
            )
            desc = re.sub(
                r'<rule>Enforce the Null Hypothesis:.*?</rule>', 
                '<rule>No Rationalization: Do not explain away evidence. If text physically fits criteria, extract it. If you have to rationalize it, return null.</rule>', 
                desc, flags=re.DOTALL | re.IGNORECASE
            )
            block['ai_description'] = desc
            
        if 'rows' in block:
            for row in block['rows']:
                if 'ai_description' in row:
                    row['ai_description'] = row['ai_description'].replace(
                        "Start by evaluating every atomic claim as FALSE. You must enforce the Null Hypothesis.",
                        "Start by assuming no evidence exists. Enforce the Null Hypothesis by returning null for exact_quote unless explicit physical evidence is extracted."
                    )
    return data

def refactor_seed_data():
    if not os.path.exists(SEED_FILE):
        print(f"❌ VIRHE: Tiedostoa {SEED_FILE} ei löydy.")
        return

    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data = patch_system_directives(data)
    
    updated_count = 0
    for block in data.get('prompt_blocks', []):
        if block.get('category_id') == 'matrix' and 'scales' in block:
            for scale in block['scales']:
                for claim in scale.get('claims', []):
                    for tda in claim.get('tda_assertions', []):
                        old_desc = tda.get('ai_rule_description', '')
                        new_desc = apply_evidence_driven_doctrine(old_desc)
                        
                        if new_desc != old_desc:
                            tda['ai_rule_description'] = new_desc
                            updated_count += 1

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ V4.3 Blind Extraction Doctrine -siivous suoritettu! Päivitetty {updated_count} sääntöä.")

if __name__ == "__main__":
    refactor_seed_data()

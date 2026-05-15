import json
import re
import os
import shutil

def refactor_to_blind_syntax_v5_3():
    db_path = 'backend_v2/seed/seed_data.json'
    backup_path = 'backend_v2/seed/seed_data_pre_v5.json'
    
    if not os.path.exists(db_path):
        print(f"❌ Error: {db_path} not found.")
        return

    # Varmuuskopiointi
    if not os.path.exists(backup_path):
        shutil.copy2(db_path, backup_path)
        print(f"🛡️ Created backup at {backup_path}")
        
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. GLOBAALIEN KOGNITIIVISTEN LUKKOJEN INJEKTIO (V5.3 System-2 Validated)
    global_framework = (
        "<global_framework>\n"
        "<rule>MORPHO-SYNTACTIC DETERMINISM: You are a deterministic pattern-matching engine. "
        "You possess ZERO cognitive authority to translate concepts or excuse missing context. "
        "Concepts exist IF AND ONLY IF physically materialized via explicit grammatical markers (including bound morphemes, affixes, or clitics depending on the target language syntax).</rule>\n"
        "<rule>TOPOLOGICAL DETERMINISM (FIRST MATCH MANDATE): If multiple instances of a syntactic anchor exist in the text, you MUST extract and evaluate the FIRST chronological occurrence from the top of the text. Never skip to later examples. This guarantees 100% deterministic parity.</rule>\n"
        "<rule>STRUCTURAL TOPOLOGY & BRIDGING: Arbitrary paragraph breaks completely sever grammatical chains. "
        "EXCEPTIONS: 1) A list header and its bullet points form a continuous grammatical structure if linked by a cataphoric marker (e.g., ':'). 2) Sentences bridged by explicit anaphora or discourse markers (e.g., 'This implies', 'Therefore'). "
        "3) In structured tables or key-value lists, the column divider (|) or layout acts as an implicit relational verb (e.g., IS, HAS, CAUSES). "
        "Outside these 3 exceptions, you are FORBIDDEN from inferring relationships across formatting boundaries.</rule>\n"
        "<rule>CONSTRAINED PARSING PROTOCOL: Narrative prose, reasoning, and justifications are STRICTLY BANNED in `mechanical_trace`. "
        "To prevent hallucination and JSON parsing errors, your trace MUST strictly follow this exact 5-step piped format using single quotes ('') for snippets and NO line breaks inside brackets:\n"
        "[1. RAW TEXT SCAN: 'exact text snippet'] | "
        "[2. SYNTACTIC ANCHOR: 'word/suffix/none'] | "
        "[3. TARGET NODE: 'word/none/N/A'] | "
        "[4. LINGUISTIC BRIDGE: 'syntax/anaphora/tabular-copula/none'] | "
        "[5. VALIDATION DECISION: Pass/Fail]</rule>\n"
        "</global_framework>"
    )

    updated_blocks = 0
    updated_atoms = 0

    for block in data.get('prompt_blocks', []):
        desc = block.get('ai_description', '')
        
        # Puhdistetaan aiemmat injektiot (Täysin idempotentti ajo)
        desc = re.sub(r'<global_framework>.*?</global_framework>\s*', '', desc, flags=re.DOTALL)
        # Puhdistetaan myös mahdolliset aiemmat V5.1/V5.2 kokeilut varmuuden vuoksi
        desc = re.sub(r'<rule>MORPHO-SYNTACTIC.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rule>TOPOLOGICAL.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rule>STRUCTURAL TOPOLOGY.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rule>ANTI-LAWYER.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rule>CONSTRAINED PARSING.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rule>GRAMMAR-BASED.*?</rule>\s*', '', desc, flags=re.DOTALL)
        desc = re.sub(r'<rules>\s*</rules>\s*', '', desc, flags=re.DOTALL)

        # Injektoidaan uusi framework blokin alkuun
        desc = f"{global_framework}\n\n{desc.strip()}"
            
        block['ai_description'] = desc
        updated_blocks += 1

        # 2. TDA-ATOMIEN MUDONMUUTOS
        if 'scales' in block:
            for scale in block.get('scales', []):
                for claim in scale.get('claims', []):
                    for tda in claim.get('tda_assertions', []):
                        rule = tda.get('ai_rule_description', '')
                        original_rule = rule
                        
                        rule = rule.replace("STEP 1 (Lexical Anchor):", "STEP 1 (Syntactic Anchor):")
                        
                        # Turvallinen regex TRACE REQUIREMENT ja ENFORCEMENT MANDATE poistamiseen
                        split_regex = r'(?i)\s*(?:TRACE REQUIREMENT|ENFORCEMENT MANDATE|ENFORCEMENT RULE):'
                        parts = re.split(split_regex, rule)
                        
                        base_rule = parts[0].strip()
                        
                        # Kahlittu lokitus
                        new_trace = (
                            "TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework."
                        )
                        
                        # UUSI MANDAATTI (Tukee negatiivisia Vice-sääntöjä)
                        new_mandate = (
                            "ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. "
                            "IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. "
                            "If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. "
                            "Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails."
                        )
                        
                        new_full_rule = f"{base_rule} {new_trace} {new_mandate}"
                        
                        if new_full_rule != original_rule:
                            tda['ai_rule_description'] = new_full_rule
                            updated_atoms += 1

    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ V5.3 System-2 Agnostic Hardening Refactor suoritettu.")
    print(f"   Päivitetty ylätason blokkeja: {updated_blocks}")
    print(f"   Päivitetty atomeja: {updated_atoms}")

if __name__ == '__main__':
    refactor_to_blind_syntax_v5_3()

import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

RULE_STRUCTURED_CONTENT = """SÄÄNTÖ 5 (Strukturoitu Tuotos):
Agentin on tuotettava vastauksensa TÄSMÄLLEEN pyydetyssä formaatissa.
- Jos pyydetään raporttia, noudata raportin rakennetta.
- Jos pyydetään JSONia, noudata JSON-skeemaa.
- Älä poikkea määritellystä rakenteesta."""

RULE_JSON_CONTENT = """SÄÄNTÖ 6 (JSON-Pakotus):
Vastauksen ON OLTAVA teknisesti validia JSON-dataa.
- Älä käytä markdown-muotoilua (kuten ```json).
- Älä lisää mitään tekstiä JSON-objektin ulkopuolelle.
- Varmista, että kaikki sulut on suljettu oikein."""

def refactor():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data['components']
    steps = data['steps']
    
    # 1. Update rule_structured_output
    struct_rule = next((c for c in components if c['id'] == 'rule_structured_output'), None)
    if struct_rule:
        struct_rule['content'] = RULE_STRUCTURED_CONTENT
        print("Updated rule_structured_output.")
    
    # 2. Create rule_json_output
    json_rule = {
        "id": "rule_json_output",
        "type": "rule",
        "name": "JSON Output Mandate",
        "content": RULE_JSON_CONTENT,
        "description": "Enforces strict JSON output."
    }
    # Check if exists, else append
    if not any(c['id'] == 'rule_json_output' for c in components):
        components.append(json_rule)
        print("Created rule_json_output.")
    else:
        # Update content if exists
        for c in components:
            if c['id'] == 'rule_json_output':
                c['content'] = RULE_JSON_CONTENT
                print("Updated rule_json_output.")

    # 3. Update Steps
    for step in steps:
        prompts = step['execution_config']['llm_prompts']
        
        # Step 9 (XAI): Ensure NO rule_json_output, ensure rule_structured_output
        if step['id'] == 'step_9_xai':
            if 'rule_json_output' in prompts:
                prompts.remove('rule_json_output')
                print(f"Removed rule_json_output from {step['id']}")
            if 'rule_structured_output' not in prompts:
                prompts.append('rule_structured_output')
                print(f"Added rule_structured_output to {step['id']}")
        
        # Steps 1-8: Ensure BOTH rule_structured_output AND rule_json_output
        else:
            if 'rule_structured_output' not in prompts:
                prompts.append('rule_structured_output')
            if 'rule_json_output' not in prompts:
                prompts.append('rule_json_output')
                print(f"Added rule_json_output to {step['id']}")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Refactor complete.")

if __name__ == "__main__":
    refactor()

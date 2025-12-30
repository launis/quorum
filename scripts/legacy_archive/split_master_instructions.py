import re
import json
import os

MANDATES_FILE = 'data/templates/mandates.j2'
RULES_FILE = 'data/templates/global_rules.j2'
OUTPUT_FILE = 'data/granular_components.json'

def parse_mandates():
    with open(MANDATES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Header
    header_match = re.match(r"(OSA 1:.*?)(?=\n\n\n1.1 Mandaatti)", content, re.DOTALL)
    header_content = header_match.group(1).strip() if header_match else ""

    components = []
    if header_content:
        components.append({
            "id": "HEADER_MANDATES",
            "type": "prompt",
            "content": header_content,
            "name": "Mandates Header"
        })

    # Extract Mandates
    mandate_matches = re.finditer(r"(1\.\d+ Mandaatti:.*?)(?=\n\n\n|\Z)", content, re.DOTALL)
    for match in mandate_matches:
        mandate_text = match.group(1).strip()
        # Extract ID from text (e.g., 1.1)
        id_match = re.search(r"1\.(\d+)", mandate_text)
        if id_match:
            mandate_num = id_match.group(1)
            components.append({
                "id": f"MANDATE_1_{mandate_num}",
                "type": "prompt",
                "content": mandate_text,
                "name": f"Mandate 1.{mandate_num}"
            })
    return components

def parse_rules():
    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Header
    header_match = re.match(r"(OSA 3:.*?)(?=\n\n\nSÄÄNTÖ 1)", content, re.DOTALL)
    header_content = header_match.group(1).strip() if header_match else ""

    components = []
    if header_content:
        components.append({
            "id": "HEADER_RULES",
            "type": "prompt",
            "content": header_content,
            "name": "Rules Header"
        })

    # Extract Rules
    rule_matches = re.finditer(r"(SÄÄNTÖ (\d+) \(.*?\):.*?)(?=\n\n|\Z)", content, re.DOTALL)
    for match in rule_matches:
        rule_text = match.group(1).strip()
        rule_num = match.group(2)
        components.append({
            "id": f"RULE_{rule_num}",
            "type": "prompt",
            "content": rule_text,
            "name": f"Rule {rule_num}"
        })
    return components

def main():
    mandate_components = parse_mandates()
    rule_components = parse_rules()
    
    all_components = mandate_components + rule_components
    
    print(f"Found {len(mandate_components)} mandate components")
    print(f"Found {len(rule_components)} rule components")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_components, f, indent=2, ensure_ascii=False)
    
    print(f"Saved granular components to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

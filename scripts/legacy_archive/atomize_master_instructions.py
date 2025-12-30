import re
import requests
import os

API_URL = "http://localhost:8000"
TEMPLATE_PATH = os.path.join("data", "templates", "master_instructions.j2")

def parse_and_create_components():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for Mandates
    # 1.1 Mandaatti: Title
    # Content...
    mandate_pattern = re.compile(r'(\d+\.\d+)\s+Mandaatti:\s+(.*?)\n(.*?)(?=\n\d+\.\d+\s+Mandaatti:|\nOSA|\Z)', re.DOTALL)
    
    # Regex for Rules
    # SÄÄNTÖ 1 (Title): Content
    rule_pattern = re.compile(r'SÄÄNTÖ\s+(\d+)\s+\((.*?)\):\s+(.*?)(?=\nSÄÄNTÖ|\nOSA|\Z)', re.DOTALL)

    # 1. Process Mandates
    print("Processing Mandates...")
    # We need to find the section "OSA 1" first to avoid false matches? 
    # The file structure is simple enough.
    
    mandates = mandate_pattern.findall(content)
    for m_num, m_title, m_content in mandates:
        comp_id = f"MANDATE_{m_num.replace('.', '_')}"
        name = f"Mandaatti {m_num}: {m_title.strip()}"
        description = f"System Mandate {m_num}"
        body = m_content.strip()
        
        # Check for citations in body to populate citation field?
        # Simple extraction: (Author Year)
        citation = ""
        citation_match = re.search(r'\(([^)]+\d{4}[^)]*)\)', body)
        if citation_match:
            citation = f"({citation_match.group(1)})"

        payload = {
            "id": comp_id,
            "name": name,
            "type": "Mandate",
            "description": description,
            "content": body,
            "citation": citation,
            "module": "core",
            "component_class": "MandateComponent"
        }
        
        create_component(payload)

    # 2. Process Rules
    print("\nProcessing Rules...")
    rules = rule_pattern.findall(content)
    for r_num, r_title, r_content in rules:
        comp_id = f"RULE_{r_num}"
        name = f"Sääntö {r_num}: {r_title.strip()}"
        description = f"Global Rule {r_num}"
        body = r_content.strip()
        
        # Check for citations
        citation = ""
        citation_match = re.search(r'\(([^)]+\d{4}[^)]*)\)', body)
        if citation_match:
            citation = f"({citation_match.group(1)})"

        payload = {
            "id": comp_id,
            "name": name,
            "type": "Rule",
            "description": description,
            "content": body,
            "citation": citation,
            "module": "core",
            "component_class": "RuleComponent"
        }
        
        create_component(payload)

def create_component(payload):
    print(f"Creating: {payload['id']}")
    try:
        res = requests.post(f"{API_URL}/config/components", json=payload)
        if res.status_code == 200:
            print("  -> Success")
        else:
            print(f"  -> Failed: {res.text}")
    except Exception as e:
        print(f"  -> Error: {e}")

if __name__ == "__main__":
    parse_and_create_components()

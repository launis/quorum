import json
import re
from tinydb import TinyDB, Query

TEMPLATE_PATH = 'data/templates/master_instructions.j2'
SEED_PATH = 'data/seed_data.json'
DB_PATH = 'data/db.json'

def sync_rules():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    # Regex for Mandates: "1.1 Mandaatti: Name\nContent..."
    # Regex for Rules: "SÄÄNTÖ 1 (Name): Content..."
    
    components = []
    
    # 1. Parse Mandates
    # Pattern: 1.X Mandaatti: [Name]\n[Content until next header or double newline]
    # Actually, the content continues until the next "1.X Mandaatti" or "OSA X" or "SÄÄNTÖ X".
    
    # Let's split by double newlines to get blocks, then analyze.
    # Or better, use regex to find the start of each item.
    
    # Mandates
    mandate_matches = re.finditer(r'(\d\.\d) Mandaatti: (.*?)\n(.*?)(?=\n\d\.\d Mandaatti|\nOSA|\nSÄÄNTÖ|$)', text, re.DOTALL)
    
    for match in mandate_matches:
        num = match.group(1)
        name_suffix = match.group(2).strip()
        content = match.group(3).strip()
        
        comp_id = f"MANDATE_{num.replace('.', '_')}"
        name = f"Mandaatti {num}: {name_suffix}"
        
        # Clean content: Ensure it starts with KÄSKE or VAATIMUS if possible, 
        # but the template has it right after newline.
        
        components.append({
            "id": comp_id,
            "name": name,
            "type": "Mandate",
            "content": content,
            "module": "core",
            "class": "MandateComponent"
        })
        print(f"Parsed {comp_id}")

    # Rules
    # Pattern: SÄÄNTÖ X (Name): Content
    # Note: Some rules have "VAATIMUS" on the same line, some on next.
    # The template has: "SÄÄNTÖ 1 (Name): VAATIMUS..."
    
    rule_matches = re.finditer(r'SÄÄNTÖ (\d+) \((.*?)\): (.*?)(?=\nSÄÄNTÖ|\nOSA|$)', text, re.DOTALL)
    
    for match in rule_matches:
        num = match.group(1)
        name_suffix = match.group(2).strip()
        content = match.group(3).strip()
        
        comp_id = f"RULE_{num}"
        name = f"Sääntö {num}: {name_suffix}"
        
        components.append({
            "id": comp_id,
            "name": name,
            "type": "Rule",
            "content": content,
            "module": "core",
            "class": "RuleComponent"
        })
        print(f"Parsed {comp_id}")

    # Update Seed Data
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    existing_map = {c.get('id'): c for c in seed_data.get('components', []) if c.get('id')}
    
    updated_count = 0
    added_count = 0
    
    for new_comp in components:
        if new_comp['id'] in existing_map:
            # Update content and name
            existing = existing_map[new_comp['id']]
            if existing.get('content') != new_comp['content'] or existing.get('name') != new_comp['name']:
                existing['content'] = new_comp['content']
                existing['name'] = new_comp['name']
                # Preserve citation if it exists, or let populate_citations handle it
                updated_count += 1
        else:
            # Add new
            seed_data['components'].append(new_comp)
            added_count += 1
            
    print(f"Updated {updated_count} components, Added {added_count} components to seed_data.json")
    
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    # Update DB
    db = TinyDB(DB_PATH)
    comps_table = db.table('components')
    Component = Query()
    
    for comp in components:
        # We need to fetch the full component from seed_data to include all fields (like citation if it was preserved)
        full_comp = next((c for c in seed_data['components'] if c.get('id') == comp['id']), comp)
        comps_table.upsert(full_comp, Component.id == comp['id'])
        
    print("Updated db.json")

if __name__ == '__main__':
    sync_rules()

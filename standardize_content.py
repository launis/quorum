import json
import re
from tinydb import TinyDB, Query

SEED_PATH = 'data/seed_data.json'
DB_PATH = 'data/db.json'

def standardize_content():
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    components = data.get('components', [])

    for comp in components:
        # Skip if no ID (shouldn't happen for valid rules/mandates but good to be safe)
        if not comp.get('id'):
            continue

        ctype = comp.get('type')
        if ctype in ['Rule', 'Mandate']:
            content = comp.get('content', '')
            name = comp.get('name', '')
            
            # 1. Clean Content: Remove leading Name or "Sääntö X" if present
            # Split by newline
            lines = content.split('\n')
            if lines:
                first_line = lines[0].strip()
                # Check if first line matches the name or looks like a title
                if first_line == name or first_line.startswith('Sääntö') or first_line.startswith('Mandaatti'):
                    # Remove the first line
                    new_content = '\n'.join(lines[1:]).strip()
                    if new_content != content:
                        comp['content'] = new_content
                        updated_count += 1
                        # print(f"Cleaned content for {comp['id']}")

            # 2. Specific Logic for Rule 2
            if comp['id'] == 'RULE_2':
                comp['citation'] = 'OWASP LLM06:2025; vrt. OWASP Foundation 2025d'
                # Ensure citation_full is populated for these if possible, or leave for populate_citations.py
                # The user didn't explicitly ask for citation_full for this specific example, 
                # but implied "varmista että kaikki... menee juuri näin".
                # I will set the citation field as requested.
                updated_count += 1
                print(f"Enforced Rule 2 formatting.")

    # Save seed data
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} components in seed_data.json")

    # Update DB
    db = TinyDB(DB_PATH)
    comps_table = db.table('components')
    Component = Query()
    
    for comp in components:
        if comp.get('type') in ['Rule', 'Mandate'] and comp.get('id'):
            comps_table.upsert(comp, Component.id == comp['id'])
            
    print("Updated components in db.json")

if __name__ == '__main__':
    standardize_content()

import json
import re
from tinydb import TinyDB, Query

SEED_PATH = 'data/seed_data.json'
DB_PATH = 'data/db.json'

def populate_citations():
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build a lookup map from Reference components
    # Key: citation (e.g., "(Acemoglu & Restrepo 2018)") -> Value: citation_full
    ref_map = {}
    for comp in data.get('components', []):
        if comp.get('type') == 'Reference':
            short_cit = comp.get('citation')
            full_cit = comp.get('citation_full')
            if short_cit and full_cit:
                # Normalize key: remove parens and extra spaces for better matching
                norm_key = short_cit.replace('(', '').replace(')', '').strip()
                ref_map[norm_key] = full_cit
                # Also map the exact string just in case
                ref_map[short_cit] = full_cit

    print(f"Loaded {len(ref_map)} reference mappings.")

    updated_count = 0
    components = data.get('components', [])

    for comp in components:
        if comp.get('type') in ['Rule', 'Mandate']:
            # Skip if already populated (like Rule 14)
            if comp.get('citation_full'):
                continue

            citation = comp.get('citation')
            if citation:
                # Handle multiple citations separated by ;
                # Example: "(Google DeepMind 2025a; Google DeepMind 2025b)"
                # We need to clean the string first
                clean_cit = citation.replace('(', '').replace(')', '')
                parts = [p.strip() for p in clean_cit.split(';')]
                
                full_citations = []
                for part in parts:
                    # Strip prefixes like "vrt." or "ks."
                    part = re.sub(r'^(vrt\.|ks\.)\s*', '', part, flags=re.IGNORECASE).strip()
                    
                    if part in ref_map:
                        full_citations.append(ref_map[part])
                    else:
                        # Try fuzzy matching or partial matching if needed
                        # For now, just warn
                        print(f"Warning: No reference found for '{part}' in component {comp.get('id')}")

                if full_citations:
                    comp['citation_full'] = "\n\n".join(full_citations)
                    updated_count += 1
                    print(f"Updated {comp.get('id')} with {len(full_citations)} citations.")

    # Save seed data
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} components in seed_data.json")

    # Update DB
    db = TinyDB(DB_PATH)
    comps_table = db.table('components')
    Component = Query()
    
    for comp in components:
        if comp.get('type') in ['Rule', 'Mandate']:
            comps_table.upsert(comp, Component.id == comp['id'])
            
    print("Updated components in db.json")

if __name__ == '__main__':
    populate_citations()

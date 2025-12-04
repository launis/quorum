import json
import re
from tinydb import TinyDB, Query

DB_PATH = 'data/db_mock.json'

def split_and_refactor():
    db = TinyDB(DB_PATH, encoding='utf-8')
    components_table = db.table('components')
    
    # Fetch all Rules and Mandates
    Component = Query()
    rules = components_table.search(Component.id.matches(r'^RULE_\d+$'))
    mandates = components_table.search(Component.id.matches(r'^MANDATE_\d+$'))
    
    all_items = rules + mandates
    
    new_components = []
    
    # Regex patterns for splitting
    # We look for keywords at the start of lines or sentences
    # Keywords: KÄSKE, VAATIMUS, KIELLETTY, ÄLÄ, HUOMIO
    
    # Strategy: Split by double newlines first to get paragraphs.
    # Then classify each paragraph.
    
    for item in all_items:
        original_id = item['id']
        content = item['content']
        
        # Split into chunks (paragraphs)
        chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
        
        for i, chunk in enumerate(chunks):
            # Determine Type
            comp_type = 'instruction' # Default
            
            upper_chunk = chunk.upper()
            
            if 'KIELLETTY' in upper_chunk or 'ÄLÄ' in upper_chunk.split(' '):
                comp_type = 'negative_constraint'
            elif 'HUOMIO' in upper_chunk:
                comp_type = 'attention'
            elif 'KÄSKE' in upper_chunk or 'VAATIMUS' in upper_chunk:
                comp_type = 'command'
            
            # Create new ID
            # e.g. RULE_13_CMD_1
            type_code = {
                'command': 'CMD',
                'negative_constraint': 'NEG',
                'attention': 'ATT',
                'instruction': 'TXT'
            }.get(comp_type, 'TXT')
            
            new_id = f"{original_id}_{type_code}_{i+1}"
            
            new_comp = {
                'id': new_id,
                'type': comp_type,
                'content': chunk,
                'name': f"{item['name']} - Part {i+1} ({comp_type})",
                'parent_id': original_id
            }
            
            new_components.append(new_comp)

    # Check for duplicates
    seen_content = {}
    unique_components = []
    duplicates = []
    
    for comp in new_components:
        # Normalize content for comparison (remove whitespace, case insensitive)
        norm_content = re.sub(r'\s+', '', comp['content']).lower()
        if norm_content in seen_content:
            duplicates.append((comp['id'], seen_content[norm_content]))
        else:
            seen_content[norm_content] = comp['id']
            unique_components.append(comp)
            
    print(f"Found {len(duplicates)} duplicates.")
    for dup in duplicates:
        print(f"  Duplicate: {dup[0]} is same as {dup[1]}")

    # Upsert new components
    for comp in unique_components:
        components_table.upsert(comp, Query().id == comp['id'])
        print(f"Upserted atomic component: {comp['id']} ({comp['type']})")

    # Verify Schemas in Steps
    steps_table = db.table('steps')
    steps = steps_table.all()
    print("\n--- Schema Verification ---")
    for step in steps:
        s_id = step.get('id')
        out_schema = step.get('output_schema')
        print(f"Step {s_id}: Output Schema = {out_schema}")
        if not out_schema:
            print(f"  WARNING: Step {s_id} missing output_schema!")

if __name__ == "__main__":
    split_and_refactor()

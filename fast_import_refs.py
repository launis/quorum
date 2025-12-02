import json
import re
from tinydb import TinyDB, Query
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add scripts dir to path to import the text if needed, 
# but easier to just read the file and extract the string.

SEED_PATH = 'data/seed_data.json'
if os.getenv("USE_MOCK_DB", "False").lower() == "true":
    DB_PATH = 'data/db_mock.json'
    print(f"Using MOCK DB: {DB_PATH}")
else:
    DB_PATH = 'data/db.json'
    print(f"Using REAL DB: {DB_PATH}")
IMPORT_SCRIPT_PATH = 'scripts/import_references.py'

def fast_import():
    # 1. Extract BIBLIOGRAPHY_TEXT
    with open(IMPORT_SCRIPT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract content between triple quotes
    match = re.search(r'BIBLIOGRAPHY_TEXT = """(.*?)"""', content, re.DOTALL)
    if not match:
        print("Could not find BIBLIOGRAPHY_TEXT")
        return
    
    bib_text = match.group(1)
    lines = bib_text.strip().split('\n')
    
    # 2. Load existing seed data
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    existing_ids = set(c.get('id') for c in seed_data.get('components', []) if c.get('id'))
    
    new_components = []
    
    print(f"Found {len(lines)} lines in bibliography.")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parsing logic (same as original)
        # Try to find the year pattern, including optional suffix (e.g. 2025a)
        match = re.search(r'(\d{4}[a-z]?)[:\.]', line)
        if match:
            year = match.group(1)
            author_part = line[:match.start()].strip()
            if author_part.endswith('.') and not author_part.endswith('ym.'):
                author_part = author_part[:-1]
                
            short_author = author_part
            
            if ';' in author_part:
                authors = author_part.split(';')
                first_author = authors[0].split(',')[0].strip()
                if len(authors) > 1:
                    short_author = f"{first_author} ym."
                else:
                    short_author = first_author
            elif '&' in author_part:
                parts = author_part.split('&')
                surnames = []
                for p in parts:
                    if ',' in p:
                        surnames.append(p.split(',')[0].strip())
                    else:
                        surnames.append(p.strip())
                short_author = " & ".join(surnames)
            elif ',' in author_part:
                 first_part = author_part.split(',')[0]
                 if " " not in first_part: 
                     short_author = first_part
                     if "ym." in author_part:
                         short_author += " ym."
                 else:
                     if "ym." in author_part:
                         short_author = author_part.split(',')[0] + " ym."
            
            short_citation = f"({short_author} {year})"
            
            # Construct ID
            safe_author = re.sub(r'[^a-zA-Z0-9]', '_', short_author).upper()
            safe_author = re.sub(r'_+', '_', safe_author).strip('_')
            safe_author = safe_author[:20]
            
            comp_id = f"REF_{safe_author}_{year}"
            
            if comp_id not in existing_ids:
                comp = {
                    "id": comp_id,
                    "name": f"Ref: {short_author} {year}",
                    "type": "Reference",
                    "description": f"Reference entry for {short_author} {year}",
                    "content": f"Reference: {short_citation}",
                    "citation": short_citation,
                    "citation_full": line,
                    "module": "references",
                    "class": "ReferenceComponent"
                }
                seed_data['components'].append(comp)
                existing_ids.add(comp_id)
                new_components.append(comp)
                # print(f"Added: {comp_id}")
    
    print(f"Added {len(new_components)} new references to seed data.")
    
    # 3. Save seed data
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    # 4. Update DB
    db = TinyDB(DB_PATH)
    comps_table = db.table('components')
    Component = Query()
    
    for comp in new_components:
        comps_table.upsert(comp, Component.id == comp['id'])
        
    print("Updated db.json with new references.")

if __name__ == '__main__':
    fast_import()

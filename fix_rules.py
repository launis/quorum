import json
import re
from tinydb import TinyDB, Query
import os
from dotenv import load_dotenv

load_dotenv()

SEED_PATH = 'data/seed_data.json'
if os.getenv("USE_MOCK_DB", "False").lower() == "true":
    DB_PATH = 'data/db_mock.json'
    print(f"Using MOCK DB: {DB_PATH}")
else:
    DB_PATH = 'data/db.json'
    print(f"Using REAL DB: {DB_PATH}")

def fix_rules():
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    components = data.get('components', [])
    updated_count = 0

    for comp in components:
        if comp.get('type') == 'Rule':
            content = comp.get('content', '')
            
            # Special handling for Rule 14 (Input-Control Ratio)
            if 'Input-Control Ratio' in content or comp.get('id') == 'RULE_14':
                comp['name'] = 'Malliriippumaton kompetenssin erottelusääntö - Input-Control Ratio'
                comp['citation'] = '(Turpin ym. 2023)'
                comp['citation_full'] = 'Turpin, Miles ym. 2023: Language models don\'t always say what they think: Unfaithful explanations in chain-of-thought prompting. Teoksessa A. Oh, T. Hashimoto & D. Blei (toim.), Advances in Neural Information Processing Systems 36. La Jolla: Neural Information Processing Systems Foundation, 21016–21033.'
                
                # Clean content: Remove the "Sääntö 14..." line if present
                # We want the content to start with "VAATIMUS..."
                match = re.search(r'(VAATIMUS \(Kaikki Agentit\):.*)', content, re.DOTALL)
                if match:
                    comp['content'] = match.group(1).strip()
                else:
                    # Fallback if regex doesn't match, try to split by newline
                    parts = content.split('\n', 1)
                    if len(parts) > 1 and 'VAATIMUS' in parts[1]:
                         comp['content'] = parts[1].strip()
            
            # General handling for other rules
            else:
                # Try to extract name from the first line if it looks like "Sääntö X: Name"
                first_line = content.split('\n')[0]
                match = re.match(r'Sääntö \d+: (.+)', first_line)
                if match:
                    extracted_name = match.group(1).strip()
                    # Update name if it's currently generic or None
                    if not comp.get('name') or comp.get('name').startswith('Sääntö'):
                         comp['name'] = extracted_name
                    
                    # Remove the first line from content
                    comp['content'] = content.split('\n', 1)[1].strip()

            updated_count += 1

    # Save seed data
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} rules in seed_data.json")

    # Update DB
    db = TinyDB(DB_PATH)
    comps_table = db.table('components')
    Component = Query()
    
    for comp in components:
        if comp.get('type') == 'Rule':
            comps_table.upsert(comp, Component.id == comp['id'])
            
    print("Updated rules in db.json")

if __name__ == '__main__':
    fix_rules()

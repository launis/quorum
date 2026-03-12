import json
import uuid
import datetime

def force_inject_db():
    # Load what we want to inject from seed_data.json
    seed_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'
    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    db_file = r'c:\src\quorum\data\db_v2.json'
    with open(db_file, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
        
    print("Injecting new prompt blocks directly into db_v2.json...")
    
    # TinyDB stores records as dicts of IDs under table name
    if 'prompt_blocks' not in db_data:
        db_data['prompt_blocks'] = {}

    db_pb = db_data['prompt_blocks']
    
    # Wipe old prompt blocks and insert exact ones from seed
    db_data['prompt_blocks'] = {}
    for i, b in enumerate(seed_data['prompt_blocks'], start=1):
        db_data['prompt_blocks'][str(i)] = b
        
    # Same for steps (so the logic workflow sees the new prompt block array)
    if 'steps' not in db_data:
        db_data['steps'] = {}
    db_data['steps'] = {}
    for i, s in enumerate(seed_data['steps'], start=1):
        db_data['steps'][str(i)] = s
        
    # And workflows
    if 'workflows' not in db_data:
        db_data['workflows'] = {}
    db_data['workflows'] = {}
    for i, w in enumerate(seed_data['workflows'], start=1):
        db_data['workflows'][str(i)] = w

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)
        
    print("Database patched manually to match seed_data.json state!")

if __name__ == '__main__':
    force_inject_db()

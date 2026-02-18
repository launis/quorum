import json
import shutil
import os
import sys

def migrate_file(filepath):
    print(f"Migrating {filepath}...")
    
    # 1. Backup
    backup_path = filepath + ".bak"
    shutil.copy2(filepath, backup_path)
    print(f"  Backup created: {backup_path}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        # Handle different structures (TinyDB vs List)
        # db.json -> {'knowledge_base': {'1': {...}, '2': {...}}}
        # seed_data.json -> {'knowledge_base': [...]}
        
        kb = data.get('knowledge_base')
        if not kb:
            print("  No knowledge_base found. Skipping.")
            return

        items = []
        is_dict = isinstance(kb, dict)
        
        if is_dict:
            items = kb.values()
        elif isinstance(kb, list):
            items = kb
        else:
            print(f"  Unknown KB type: {type(kb)}")
            return

        for item in items:
            if item.get('type') == 'reference':
                if 'term' in item:
                    # Move term -> short_citation
                    term_val = item.pop('term')
                    
                    # Only set if short_citation doesn't exist or is empty
                    if 'short_citation' not in item or not item['short_citation']:
                        item['short_citation'] = term_val
                        updated_count += 1
                    else:
                        # If both exist, keep short_citation (it's likely newer/correct)
                        # but still remove 'term' as per schema
                        pass 
                        
        print(f"  Updated {updated_count} reference items.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print("  Saved.")

    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Restoring from backup...")
        shutil.copy2(backup_path, filepath)
        sys.exit(1)

def verify_parity(file1, file2):
    print(f"Verifying parity between {file1} and {file2}...")
    # This is a loose verification: check if ID counts match and types in KB match
    # Full deep diff might be noisy due to list vs dict structure
    
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
        
    kb1 = d1.get('knowledge_base')
    kb2 = d2.get('knowledge_base')
    
    items1 = list(kb1.values()) if isinstance(kb1, dict) else kb1
    items2 = list(kb2.values()) if isinstance(kb2, dict) else kb2
    
    # Check counts
    print(f"  {file1}: {len(items1)} items")
    print(f"  {file2}: {len(items2)} items")
    
    if len(items1) != len(items2):
        print("  WARNING: Item counts differ!")
    
    # Check a sample reference
    ref1 = next((i for i in items1 if i.get('type') == 'reference'), None)
    if ref1:
        print(f"  Sample Ref ({file1}): {ref1.get('id')} -> short_citation='{ref1.get('short_citation')}', term='{ref1.get('term')}'")
    
    ref2 = next((i for i in items2 if i.get('type') == 'reference'), None)
    if ref2:
        print(f"  Sample Ref ({file2}): {ref2.get('id')} -> short_citation='{ref2.get('short_citation')}', term='{ref2.get('term')}'")

if __name__ == "__main__":
    db_path = "c:/src/quorum/data/db.json"
    seed_path = "c:/src/quorum/backend/seed/seed_data.json"
    
    if os.path.exists(db_path):
        migrate_file(db_path)
    else:
        print(f"File not found: {db_path}")
        
    if os.path.exists(seed_path):
        migrate_file(seed_path)
    else:
        print(f"File not found: {seed_path}")
        
    verify_parity(db_path, seed_path)

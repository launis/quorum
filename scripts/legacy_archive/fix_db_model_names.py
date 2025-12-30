import json
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'db.json')

def fix_db():
    print(f"Reading {DB_PATH}...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    system_config = db.get('system_config', {})
    updated = False

    for key, val in system_config.items():
        if val.get('type') == 'model_registry':
            print(f"Found model registry at key: {key}")
            if 'models' in val and 'google' in val['models']:
                # Update FAST strategy
                if 'fast' in val['models']['google']:
                    old_fast = val['models']['google']['fast'].get('model_name')
                    val['models']['google']['fast']['model_name'] = 'gemini-2.5-flash'
                    val['models']['google']['fast']['max_tokens'] = 16384
                    print(f"Updated FAST: {old_fast} -> gemini-2.5-flash (max_tokens=16384)")
                
                # Update DEEP strategy
                if 'deep' in val['models']['google']:
                    old_deep = val['models']['google']['deep'].get('model_name')
                    val['models']['google']['deep']['model_name'] = 'gemini-2.5-flash'
                    val['models']['google']['deep']['max_tokens'] = 16384
                    print(f"Updated DEEP: {old_deep} -> gemini-2.5-flash (max_tokens=16384)")
                
                updated = True

    if updated:
        print("Saving changes to data/db.json...")
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(db, f, separators=(',', ':')) # Minified to match style
        print("Done!")
    else:
        print("No model registry found to update.")

if __name__ == "__main__":
    fix_db()

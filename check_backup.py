import json

def check_backup():
    path = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    print(f"Checking {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        comps = data.get('components', [])
        print(f"Components Count: {len(comps)}")
        kb_found = False
        for c in comps:
             if c.get('id') == 'knowledge_base' or c.get('type') == 'knowledge_base':
                 print("KB FOUND in Backup!")
                 kb_found = True
                 break
        if not kb_found:
            print("KB NOT FOUND in Backup.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_backup()

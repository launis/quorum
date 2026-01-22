import json

def diff_comps():
    path_bak = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    path_cur = 'c:/src/quorum/backend/seed/seed_data.json'
    
    with open(path_bak, 'r', encoding='utf-8') as f:
        bak = json.load(f).get('components', [])
    with open(path_cur, 'r', encoding='utf-8') as f:
        cur = json.load(f).get('components', [])
        
    bak_ids = [c.get('id', 'N/A') + ':' + c.get('type', 'N/A') for c in bak if isinstance(c, dict)]
    cur_ids = [c.get('id', 'N/A') + ':' + c.get('type', 'N/A') for c in cur if isinstance(c, dict)]
    
    print(f"Backup Count: {len(bak_ids)}")
    print(f"Current Count: {len(cur_ids)}")
    
    diff = set(bak_ids) - set(cur_ids)
    print(f"Items in Backup but NOT in Current: {diff}")

if __name__ == "__main__":
    diff_comps()

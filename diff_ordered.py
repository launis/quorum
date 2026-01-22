import json

def diff_ordered():
    path_bak = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    path_cur = 'c:/src/quorum/backend/seed/seed_data.json'
    
    with open(path_bak, 'r', encoding='utf-8') as f:
        bak = json.load(f).get('components', [])
    with open(path_cur, 'r', encoding='utf-8') as f:
        cur = json.load(f).get('components', [])
        
    print(f"Backup: {len(bak)}, Current: {len(cur)}")
    
    for i in range(max(len(bak), len(cur))):
        b = bak[i] if i < len(bak) else None
        c = cur[i] if i < len(cur) else None
        
        bid = b.get('id', 'N/A') if b else 'NONE'
        cid = c.get('id', 'N/A') if c else 'NONE'
        
        if bid != cid:
            print(f"Mismatch at index {i}: Backup ID='{bid}' vs Current ID='{cid}'")
            if b:
                print(f"Backup Item Content: {str(b)[:200]}")
            break

if __name__ == "__main__":
    diff_ordered()

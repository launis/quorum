import json
import shutil

def restore_kb_index():
    backup_path = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    current_path = 'c:/src/quorum/backend/seed/seed_data.json'
    
    print("Loading backup...")
    with open(backup_path, 'r', encoding='utf-8') as f:
        backup = json.load(f)
        
    print("Loading current...")
    with open(current_path, 'r', encoding='utf-8') as f:
        current = json.load(f)
        
    # Get KB from Backup Index 0
    if 'components' in backup and len(backup['components']) > 0:
        kb_candidate = backup['components'][0]
        cid = kb_candidate.get('id')
        print(f"Backup Index 0 ID: {cid}")
        
        if cid == 'knowledge_base' or kb_candidate.get('type') == 'knowledge_base':
            # Check if exists in current
            exists = False
            for c in current.get('components', []):
                if c.get('id') == cid:
                    exists = True
                    break
            
            if not exists:
                print("Injecting KB at Index 0 of Current...")
                current['components'].insert(0, kb_candidate)
                
                # Save
                shutil.copy(current_path, current_path + ".bak_kb_restore")
                with open(current_path, 'w', encoding='utf-8') as f:
                    json.dump(current, f, indent=4, ensure_ascii=False)
                print("Saved restored seed_data.json.")
            else:
                print("KB already exists in current.")
        else:
            print("Backup Index 0 is NOT KB. Aborting.")
    else:
        print("Backup components empty.")

if __name__ == "__main__":
    restore_kb_index()

import json
import urllib.request

def restore_scales():
    url = 'https://raw.githubusercontent.com/launis/quorum/main/backend_v2/seed/seed_data.json'
    print("Fetching remote seed_data.json...")
    with urllib.request.urlopen(url) as response:
        remote_data = json.loads(response.read().decode())
        
    print("Loading local seed_data.json...")
    local_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    with open(local_path, 'r', encoding='utf-8') as f:
        local_data = json.load(f)
        
    # Build dictionary of remote scales by block slug
    remote_scales = {}
    for pb in remote_data.get('prompt_blocks', []):
        slug = pb.get('slug')
        if slug in ['matrix_causal_analyst', 'matrix_archivist']:
            remote_scales[slug] = pb.get('scales', [])
            
    # Replace in local
    updated = False
    for pb in local_data.get('prompt_blocks', []):
        slug = pb.get('slug')
        if slug in remote_scales:
            old_len = len(pb.get('scales', []))
            pb['scales'] = remote_scales[slug]
            new_len = len(pb['scales'])
            print(f"Updated {slug}: replaced {old_len} scales with {new_len} scales.")
            updated = True
            
    if updated:
        with open(local_path, 'w', encoding='utf-8') as f:
            json.dump(local_data, f, indent=4, ensure_ascii=False)
        print("Successfully saved local seed_data.json.")
    else:
        print("No updates made.")

if __name__ == "__main__":
    restore_scales()

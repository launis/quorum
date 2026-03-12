import json

def update_coach():
    target_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for b in data.get('prompt_blocks', []):
        if b['id'] == 'block_taskcoach':
            print(f"Old type: {b['type']}")
            b['type'] = 'string'
            
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Updated {target_file} successfully.")

if __name__ == '__main__':
    update_coach()

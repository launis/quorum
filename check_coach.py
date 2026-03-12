import json

def read_db():
    with open('data/db_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for b in data.get('prompt_blocks', []):
        if b['id'] == 'block_taskcoach':
            print(f"block_taskcoach -> type: {b.get('type')}, category_id: {b.get('category_id')}")
            
if __name__ == '__main__':
    read_db()

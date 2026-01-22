import json

def find_path():
    path = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    def search(obj, path_str="root"):
        if isinstance(obj, dict):
            if obj.get('type') == 'knowledge_base':
                print(f"FOUND KB at {path_str}. ID: {obj.get('id')}")
                return
            for k, v in obj.items():
                search(v, f"{path_str}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search(item, f"{path_str}[{i}]")

    search(data)

if __name__ == "__main__":
    find_path()

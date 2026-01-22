import json

def find_kb_content():
    path = 'c:/src/quorum/data/db.json'
    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Recursive search for "Abductive Reasoning"
    def search(obj, path_str="root"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "Abductive Reasoning":
                    print(f"FOUND 'Abductive Reasoning' key at {path_str}.{k}")
                    return True
                if search(v, f"{path_str}.{k}"):
                    return True
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if search(item, f"{path_str}[{i}]"):
                    return True
        return False

    search(data)

if __name__ == "__main__":
    find_kb_content()

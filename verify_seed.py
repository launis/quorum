import json

def deep_count(obj):
    if isinstance(obj, dict):
        count = sum(deep_count(v) for v in obj.values())
        return len(obj) + count
    elif isinstance(obj, list):
        count = sum(deep_count(v) for v in obj)
        return len(obj) + count
    else:
        return 1

def main():
    try:
        with open('backend/seed/seed_data.backup.json', 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            
        with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f)
            
        backup_count = deep_count(backup_data)
        new_count = deep_count(new_data)
        
        print(f"Backup keys/values/items count: {backup_count}")
        print(f"New data keys/values/items count: {new_count}")
        print(f"Delta: +{new_count - backup_count}")
        
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    main()

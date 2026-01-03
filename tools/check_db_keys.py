
import json

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"

def check_keys():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Top level keys: {list(data.keys())}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_keys()

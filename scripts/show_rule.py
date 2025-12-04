import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def show_rule():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comp = next((c for c in data['components'] if c['id'] == 'rule_structured_output'), None)
    if comp:
        print(f"Content: {comp['content']}")

if __name__ == "__main__":
    show_rule()

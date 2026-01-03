import json

try:
    with open(r'c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json', 'r', encoding='utf-8') as f:
        json.load(f)
    print("JSON is valid.")
except Exception as e:
    print(f"JSON Error: {e}")

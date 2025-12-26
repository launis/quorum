from tinydb import TinyDB
import json

def inspect_db():
    db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(db_path)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    print(f"Loaded {len(items)} items from KB.")
    
    # 1. Look for Strathern
    print("\n--- Searching for 'Strathern' ---")
    found_s = False
    for item in items:
        s_dump = str(item).lower()
        if 'strathern' in s_dump:
            print(f"Found in Item ID: {item.get('id', 'Unknown')}")
            print(f"Type: {item.get('type')}")
            print(f"Term: {item.get('term', '')}")
            print(f"Citation: {item.get('citation', '')}")
            found_s = True
            
    if not found_s:
        print("Strathern NOT found in DB dump.")

    # 2. Look for Confirmation Bias
    print("\n--- Searching for 'Confirmation Bias' / 'Vahvistusharha' ---")
    found_c = False
    terms_to_check = ['confirmation bias', 'vahvistusharha']
    for t in terms_to_check:
        for item in items:
            if item.get('term', '').lower() == t:
                print(f"Found Concept: {item.get('term')}")
                print(f"Definition: {item.get('definition')}")
                found_c = True
    if not found_c:
        print("Confirmation Bias concept NOT found.")

if __name__ == "__main__":
    inspect_db()

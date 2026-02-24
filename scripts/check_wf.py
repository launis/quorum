import json

def get_wf_from_db():
    try:
        data = json.load(open('c:/src/quorum/backend/seed/seed_data.json', encoding="utf-8"))
        wf = next((w for w in data.get('workflows', []) if w.get('id') == 'ca09d8a4-a694-4aab-95d0-770535d44f85'), None)
        
        if wf:
            print(f"Name: {wf.get('name')}")
            for sid in wf.get('steps', []):
                if isinstance(sid, str):
                    found = False
                    for collection in ['steps', 'components', 'agents', 'matrices']:
                        col_data = data.get(collection, [])
                        if isinstance(col_data, list):
                            for item in col_data:
                                if item.get('id') == sid:
                                    print(f"{sid} -> {collection}: {item.get('name') or item.get('slug')}")
                                    found = True
                    if not found:
                        print(f"{sid} -> NOT FOUND in seed_data")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_wf_from_db()

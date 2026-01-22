import json

def check_db_comps():
    path = 'c:/src/quorum/data/db.json'
    print(f"Checking {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'components' in data:
        comps = data['components']
        print(f"Components Type: {type(comps)}")
        if isinstance(comps, dict):
            print(f"Keys Count: {len(comps)}")
            # Search for KB
            found = False
            for k, v in comps.items():
                if v.get('id') == 'knowledge_base' or v.get('type') == 'knowledge_base':
                    print(f"FOUND KB at Key '{k}'! ID: {v.get('id')}")
                    found = True
            
            if not found:
                print("KB NOT FOUND in components dict values.")
                # check for key '2'
                if '2' in comps:
                     print(f"Key '2' exists. Content: {str(comps['2'])[:100]}")
                else:
                    print("Key '2' DOES NOT exist.")
        elif isinstance(comps, list):
            print(f"List length: {len(comps)}")
            # ...
    else:
        print("No components in DB")

if __name__ == "__main__":
    check_db_comps()

import json
from pathlib import Path
from tinydb import TinyDB

def check_databases():
    db_path = Path("data/db.json")
    mock_db_path = Path("data/db_mock.json")
    
    print(f"Checking {db_path}...")
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
        
    print(f"Checking {mock_db_path}...")
    with open(mock_db_path, 'r', encoding='utf-8') as f:
        mock_data = json.load(f)

    # TinyDB structure: {"components": {"1": {...}, "2": {...}}}
    
    def analyze_table(data, table_name, db_name):
        if table_name not in data:
            print(f"WARNING: Table '{table_name}' not found in {db_name}")
            return {}
            
        table = data[table_name]
        print(f"--- {db_name} / {table_name} ---")
        print(f"Total items: {len(table)}")
        
        items = {}
        for key, item in table.items():
            if 'id' not in item or item['id'] is None:
                print(f"  [MISSING ID] Internal Key: {key}, Content: {item}")
            
            items[item.get('id', 'NO_ID')] = item
            
            # Check for None/null values
            for k, v in item.items():
                if v is None:
                    print(f"  [NULL] Item ID: {item.get('id')} Key: {k} is null")
                if v == "None":
                    print(f"  ['None'] Item ID: {item.get('id')} Key: {k} is string 'None'")
                if v == "":
                    # Empty strings are allowed but good to know
                    pass
        return items

    db_comps = analyze_table(db_data, 'components', 'PROD DB')
    mock_comps = analyze_table(mock_data, 'components', 'MOCK DB')
    
    # Compare
    print("\n--- Comparison ---")
    all_ids = set(db_comps.keys()) | set(mock_comps.keys())
    
    identical = True
    for cid in all_ids:
        if cid not in db_comps:
            print(f"MISSING in PROD: {cid}")
            identical = False
            continue
        if cid not in mock_comps:
            print(f"MISSING in MOCK: {cid}")
            identical = False
            continue
            
        # Compare content
        prod_c = db_comps[cid]
        mock_c = mock_comps[cid]
        
        # Ignore internal TinyDB ID if present (usually not in item dict unless inserted)
        
        if prod_c != mock_c:
            print(f"DIFFERENCE in {cid}:")
            print(f"  PROD: {prod_c}")
            print(f"  MOCK: {mock_c}")
            identical = False
            
    if identical:
        print("Databases are IDENTICAL regarding components.")
    else:
        print("Databases are DIFFERENT.")

if __name__ == "__main__":
    check_databases()

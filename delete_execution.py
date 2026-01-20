
import json
import sys

def delete_exec(target_id):
    db_path = r'c:\src\quorum\data\db.json'
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # TinyDB usually stores data in tables. 
        # If 'executions' is a top level key, it might be a dict of ID -> Item
        # OR it might be TinyDB format: {"executions": {"1": {id: ...}, "2": {id: ...}}}
        
        executions_table = data.get('executions', {})
        
        keys_to_delete = []
        found = False
        
        # Scenario A: Dict of ID -> Item
        if target_id in executions_table:
            keys_to_delete.append(target_id)
            found = True
        else:
            # Scenario B: TinyDB numeric keys
            for key, val in executions_table.items():
                if val.get('id') == target_id:
                    keys_to_delete.append(key)
                    found = True
                    # Don't break, in case of duplicates? TinyDB usually unique IDs but...
        
        if found:
            print(f"Found {len(keys_to_delete)} entries for ID {target_id}. Deleting...")
            for k in keys_to_delete:
                del executions_table[k]
            
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Deletion successful.")
        else:
            print(f"ID {target_id} NOT found in 'executions' table.")
            # Debug: Print first few IDs
            ids = []
            for v in list(executions_table.values())[:5]:
                 ids.append(v.get('id', 'Unknown'))
            print(f"Sample available IDs: {ids}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_exec('7a0cd46d-e2ab-49ad-a7b1-21960dee037a')

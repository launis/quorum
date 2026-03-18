import json
import os

db_path = r'C:\src\quorum\data\db_v2.json'
out_path = r'C:\src\quorum\LATEST_EXECUTION_EXPORT.json'

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    execs = []
    
    for table_name, table_data in db.items():
        if isinstance(table_data, dict):
            for doc_id, doc in table_data.items():
                if isinstance(doc, dict) and 'id' in doc and doc['id'].startswith('exe_'):
                    execs.append(doc)

    if not execs:
        print("NO EXECUTIONS FOUND IN DB")
    else:
        # Sort by creation / completion time chronologically (latest first)
        def get_time(e):
            return e.get('completed_at') or e.get('created_at') or ''
        
        execs.sort(key=get_time, reverse=True)
        latest = execs[0]

        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(latest, out, indent=2, ensure_ascii=False)
        print(f"SUCCESS: Exported {latest['id']} to {out_path}")

except Exception as e:
    print(f"ERROR: {e}")

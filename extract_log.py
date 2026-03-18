import json
import os

target_id = 'exe_67bb5d96c35c4335883efc1fd7566a50'
found_text = None

for db_name in ['db_v2.json', 'db.json']:
    path = os.path.join(r'C:\src\quorum\data', db_name)
    if not os.path.exists(path):
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            db = json.load(f)
            
        execs = db.get('executions', {})
        if isinstance(execs, dict):
            for k, v in execs.items():
                if v.get('id') == target_id:
                    found_text = v.get('state_data', {}).get('inputs', {}).get('chat_log')
                    break
        elif isinstance(execs, list):
            for v in execs:
                if v.get('id') == target_id:
                    found_text = v.get('state_data', {}).get('inputs', {}).get('chat_log')
                    break
        if found_text:
            break
    except Exception as e:
        print(f"Error reading {db_name}: {e}")

if found_text:
    with open(r'c:\src\quorum\extracted_chat.md', 'w', encoding='utf-8') as f:
         f.write(found_text)
    print("SUCCESS")
else:
    print("NOT FOUND")

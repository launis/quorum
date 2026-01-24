
import json

db_path = r"c:\src\quorum\data\db.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    for eid, details in executions.items():
        dump = json.dumps(details)
        if "83.3" in dump:
            print(f"Found match via String Search: Key {eid} (ID: {details.get('id')})")
            
            # Try to pinpoint location
            res = details.get("results", {})
            judge = res.get("step_results", {}).get("step_judge", {}).get("output", {})
            print(f"Judge Keys: {judge.keys()}")
            score_cards = judge.get("score_cards")
            if score_cards:
                print("Score Cards Found.")
            else:
                print("Score Cards Missing.")

except Exception as e:
    print(f"Error: {e}")

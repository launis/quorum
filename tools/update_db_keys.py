import json
import os

DB_PATH = 'c:\\Users\\risto\\OneDrive\\quorum\\data\\db_mock.json'

def update_db_keys():
    if not os.path.exists(DB_PATH):
        print(f"File not found: {DB_PATH}")
        return

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    # Iterate through executions
    executions = data.get('executions', {})
    for exec_id, execution in executions.items():
        # Iterate through steps in the execution history if present?
        # Actually in db_mock.json structure, 'executions' stores the WorkflowExecution object
        # which has 'history' or 'results'? 
        # Let's inspect the structure from my previous view.
        # It seems 'executions' is a dict of executions.
        # But wait, looking at my view of db_mock.json in Step 464:
        # "executions": {"1": { ... "result": { ... "step_8_judge": { ... "pisteet": { ... } } } } }
        
        # It seems the result is nested in the execution object.
        
        result_blob = execution.get('result')
        if not result_blob:
            continue
            
        step_8_judge = result_blob.get('step_8_judge')
        if step_8_judge:
            pisteet = step_8_judge.get('pisteet')
            if pisteet:
                # Rename keys
                changed = False
                mappings = {
                    'analyysi_ja_prosessi': 'analyysi',
                    'arviointi_ja_argumentaatio': 'arviointi',
                    'synteesi_ja_luovuus': 'synteesi'
                }
                
                for old_key, new_key in mappings.items():
                    if old_key in pisteet:
                        pisteet[new_key] = pisteet.pop(old_key)
                        changed = True
                
                if changed:
                    updated_count += 1
                    print(f"Updated keys in execution {exec_id}, step_8_judge")

    if updated_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully updated {updated_count} execution records in {DB_PATH}")
    else:
        print("No records needed updating.")

if __name__ == "__main__":
    update_db_keys()

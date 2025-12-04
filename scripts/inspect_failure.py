from tinydb import TinyDB
import json

def inspect_failure():
    db = TinyDB('data/db_mock.json', encoding='utf-8')
    executions = db.table('executions')
    all_execs = executions.all()
    
    if not all_execs:
        print("No executions found.")
        return

    latest = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]
    
    print(f"ID: {latest.doc_id}")
    print(f"Status: {latest.get('status')}")
    print(f"Current Step: {latest.get('current_step')}")
    print(f"Error: {latest.get('error')}")
    
    steps = latest.get('step_results', [])
    print(f"Steps completed: {len(steps)}")
    
    if steps:
        last_step = steps[-1]
        print(f"Last Step ID: {last_step.get('step_id')}")
        # Print output keys to see what we got
        output = last_step.get('output')
        if isinstance(output, dict):
            print(f"Last Output Keys: {list(output.keys())}")
        else:
            print(f"Last Output Type: {type(output)}")
            print(f"Last Output Preview: {str(output)[:200]}")

if __name__ == "__main__":
    inspect_failure()

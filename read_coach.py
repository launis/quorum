import json

def read_db():
    with open('data/db_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    execs = data.get('executions', {})
    if not execs:
        return
        
    # Get the latest execution
    latest_k = list(execs.keys())[-1]
    results = execs[latest_k].get('results', {})
    
    print(f"--- execution_id: {latest_k} ---")
    print(f"Available keys in result: {list(results.keys())}")
    if 'step_coach' in results:
        print("STEP_COACH OUTPUT:")
        print(json.dumps(results['step_coach'], indent=2))
            
if __name__ == '__main__':
    read_db()

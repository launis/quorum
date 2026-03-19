import json

def analyze():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    executions = db.get('executions', {})
    if not executions:
        print('No executions in DB.')
        return

    # executions is a dict. get the last item
    latest_id = list(executions.keys())[-1]
    latest = executions[latest_id]
    print(f'Execution ID: {latest_id}')
    
    results = latest.get('results', {})
    if not results:
        print('No results in this execution.')
        return

    for phase, data in results.items():
        print(f'\n--- Phase: {phase} ---')
        if not isinstance(data, dict):
             continue
        for k, v in data.items():
            if isinstance(v, (int, float)):
                just_key = f'{k}_justification'
                val_type = type(v).__name__
                
                # If there's a justification key matching the score
                if just_key in data:
                    just = data[just_key]
                    print(f'{k}: {v} ({val_type})')
                    # print(f'   Justification snippet: {str(just).replace(chr(10), " ")[:80]}...')
                # Or maybe it's the 100-scale master score
                elif 'score' in k.lower() or 'percent' in k.lower():
                    print(f'{k}: {v} ({val_type})')

if __name__ == '__main__':
    analyze()

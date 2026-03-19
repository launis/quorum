import json

def analyze():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    executions = db.get('executions', {})
    latest_id = list(executions.keys())[-1]
    latest = executions[latest_id]
    
    results = latest.get('results', {})
    for phase, data in results.items():
        if not isinstance(data, dict): continue
        if 'blk_371c7724eeba40218409b5a3697ac1d3' in data:
            print("TOULMIN SCORE:", data['blk_371c7724eeba40218409b5a3697ac1d3'])
            print("TOULMIN JUSTIFICATION:", data.get('blk_371c7724eeba40218409b5a3697ac1d3_justification'))

if __name__ == '__main__':
    analyze()

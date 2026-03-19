import json

def run():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    executions = db.get('executions', {})
    if not executions: return
    latest_id = list(executions.keys())[-1]
    wf_id = executions[latest_id].get("workflow_id")
    
    wf = next((w for w in db.get('v2_workflows', []) if w.get('id') == wf_id), None)
    if not wf: return
    
    bp_id = wf.get('blueprint_id')
    bp = next((b for b in db.get('blueprints', []) if b.get('id') == bp_id), None)
    if not bp: return
    
    print(json.dumps(bp, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    run()

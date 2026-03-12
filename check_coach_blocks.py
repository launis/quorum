import json

def check_coach_blocks():
    target_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    wf = next(w for w in data['workflows'] if w['id'] == 'workflow_courtroom_20_full_audit')
    coach_step = next(s for s in wf['steps'] if s['task_blueprint'] == 'step_coach')
    
    print("--- COACH PROMPT BLOCKS ---")
    for b_id in coach_step.get('prompt_blocks', []):
        b = next((x for x in data['prompt_blocks'] if x['id'] == b_id), None)
        if b:
            print(f"{b_id}: type={b.get('type')}")
        else:
            print(f"{b_id}: NOT FOUND!")

if __name__ == '__main__':
    check_coach_blocks()

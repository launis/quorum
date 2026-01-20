
import json
import sys
from typing import Dict, Any

def inspect_execution(target_id: str):
    db_path = r'c:\src\quorum\data\db.json'
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        executions = db_data.get('executions', {})
        # Search by ID field (TinyDB style)
        for key, val in executions.items():
            if val.get('id') == target_id:
                target_exec = val
                print(f"Found execution under key: {key}")
                break
        
        if not target_exec:
             # Try direct key lookup as fallback
             target_exec = executions.get(target_id)

        if not target_exec:
            print(f"Execution {target_id} NOT FOUND in db.json")
            print(f"Total executions: {len(executions)}")
            print(f"Available IDs: {list(executions.keys())}")
            # Check for near matches
            for key in executions.keys():
                if target_id in key or key in target_id:
                    print(f"Did you mean: {key}?")
            return

        print(f"=== Execution {target_id} ===")
        print(f"Status: {target_exec.get('status')}")
        print(f"Workflow ID: {target_exec.get('workflow_id')}")
        
        results = target_exec.get('results', {})
        if "step_results" in results:
            steps = results["step_results"]
            print("Format: Standard (step_results found)")
        else:
            steps = results
            print("Format: Flat/Legacy")

        # Check Judge
        judge = steps.get("step_judge") or steps.get("step_judge_cognitive")
        if judge:
            print(f"\n[Judge Step Found]")
            print(f"Matrix ID (in step): {judge.get('matrix_id')}")
            print(f"Matrix ID (in metadata): {judge.get('metadata', {}).get('matrix_id')}")
            
            # Scores
            if "score_cards" in judge:
                 print(f"Score Cards: {json.dumps(judge['score_cards'], indent=2)}")
            elif "pisteet" in judge:
                 print(f"Pisteet: {judge['pisteet']}")
            else:
                 print("No scores found.")
                 
            # Resolve Matrix Scale Logic
            matrix_id = judge.get('matrix_id') or judge.get('metadata', {}).get('matrix_id')
            if not matrix_id:
                # Fallback to workflow
                wf_id = target_exec.get('workflow_id')
                wf = db_data.get('workflows', {}).get(wf_id, {})
                for s in wf.get('steps', []):
                    if s.get('task_key') in ['judge', 'cognitive_judge']:
                        matrix_id = s.get('config', {}).get('matrix_id')
                        print(f"Matrix ID resolved from Workflow: {matrix_id}")
                        break
            
            if matrix_id:
                matrix = db_data.get('components', {}).get(matrix_id)
                # handle tinydb generic matching if needed, but usually key is ID
                if not matrix:
                     for v in db_data.get('components', {}).values():
                         if v.get('id') == matrix_id:
                             matrix = v
                             break
                
                if matrix:
                    print(f"\n[Matrix Component: {matrix_id}]")
                    content = matrix.get("content", {})
                    if "scale" in content:
                        print(f"Content.Scale: {content['scale']}")
                    elif "scale" in matrix:
                         print(f"Root.Scale (Legacy): {matrix['scale']}")
                    else:
                        print("No scale found in matrix.")
                else:
                    print(f"Matrix component {matrix_id} NOT found in DB.")
        else:
            print("No judge step found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_execution('e751e9dd-afb4-423b-a7a5-197d465b9dd0')

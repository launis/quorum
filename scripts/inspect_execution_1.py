
import json
import os

db_path = r"c:\src\quorum\data\db.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get('executions', {})
    if '1' in executions:
        run = executions['1']
        print(f"--- Execution 1 ---")
        print(f"Status: {run.get('status')}")
        print(f"Workflow ID: {run.get('workflow_id')}")
        
        # Check inputs
        print(f"Inputs: {list(run.get('inputs', {}).keys())}")
        
        # Check Step Trace
        traces = run.get('step_trace', [])
        print(f"Step Trace Count: {len(traces)}")
        
        for step in traces:
            s_id = step.get('step_id')
            s_status = step.get('status')
            s_output = step.get('output')
            print(f"Step: {s_id} | Status: {s_status}")
            
            if s_id == 'step_judge':
                print(f"   [JUDGE OUTPUT KEYS]: {list(s_output.keys()) if isinstance(s_output, dict) else s_output}")
                if isinstance(s_output, dict):
                    print(f"   [JUDGE SCORE]: {s_output.get('pisteet')}")
                    print(f"   [JUDGE MATRIX]: {s_output.get('matrix')}")
            
            if s_id == 'step_xai':
                print(f"   [XAI OUTPUT]: {str(s_output)[:200]}...") # Print beginning
                
except Exception as e:
    print(f"Error: {e}")

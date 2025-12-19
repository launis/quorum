
import json
import os

file_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get('executions', {})
    
    target_ids = ['bdcd4fe5-2706-427d-9534-329eb502fd4e', 'dddd03d0-2cb0-43b9-bc6d-aedbb285f9ca']
    
    print(f"Total executions: {len(executions)}")
    
    for key, output in executions.items():
        exec_id = output.get('execution_id')
        if exec_id in target_ids:
            print(f"\n--- Execution: {exec_id} ---")
            print(f"Status: {output.get('status')}")
            
            # Check step_coach output
            trace = output.get('trace', {})
            step_coach = trace.get('step_coach')
            
            if step_coach:
                print("Step Coach Output found.")
                print("Lahdeluettelo:", step_coach.get('lahdeluettelo'))
                print("Oppimispolku:", step_coach.get('oppimispolku_viikko'))
            else:
                print("Step Coach trace NOT found.")
                
            # Also check if it's currently in trace of a running job
            if output.get('status') == 'running':
                print("Job is RUNNING. Checking current trace...")
                # The 'trace' field in top-level execution object IS the current state for running jobs?
                # or is it in 'details'? 
                # In TinyDB logic, we update the document.
                pass
                
except Exception as e:
    print(f"Error parsing DB: {e}")

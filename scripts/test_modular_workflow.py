import requests
import time
import os
import json

API_URL = "http://localhost:8000"

def test_modular_workflow():
    print("1. Skipping upload (using dummy text)...")
    
    workflow_id = "sequential_audit_chain"
    
    print(f"4. Executing Workflow {workflow_id}...")
    inputs = {
        "prompt_text": "Dummy Prompt",
        "history_text": "Dummy History",
        "product_text": "Dummy Product",
        "reflection_text": "Dummy Reflection"
    }
    
    try:
        res = requests.post(f"{API_URL}/executions", json={"workflow_id": workflow_id, "initial_inputs": inputs})
        if res.status_code != 200:
            print(f"Failed to start execution: {res.text}")
            return
            
        execution_id = res.json()['execution_id']
        print(f"   Execution started with ID: {execution_id}")

        print("5. Polling for completion...")
        while True:
            res = requests.get(f"{API_URL}/executions/{execution_id}")
            data = res.json()
            status = data['status']
            print(f"   Status: {status} - Step: {data.get('current_step', 'N/A')}")
            
            if status == 'completed':
                print("\nWorkflow Completed Successfully!")
                
                # Check for XAI Report Hoisted Fields
                result = data.get('result', {})
                
                hoist_check = {
                    "Executive Summary": result.get('executive_summary'),
                    "Final Verdict": result.get('final_verdict'),
                    "Confidence Score": result.get('confidence_score'),
                    "Detailed Analysis": result.get('detailed_analysis'),
                    "Formatted Report (from Hook)": result.get('xai_report_formatted')
                }
                
                print("\n--- XAI Report Verification ---")
                all_found = True
                for key, val in hoist_check.items():
                    status_icon = "✅ Found" if val else "❌ MISSING"
                    content_preview = str(val)[:50].replace('\n', ' ') + "..." if val else "N/A"
                    print(f"{key}: {status_icon} | Content: {content_preview}")
                    if not val: all_found = False
                
                if all_found:
                    print("\nSUCCESS: All Report fields are present!")
                else:
                    print("\nFAILURE: Some Report fields are missing.")

                break

            elif status == 'failed':
                print(f"\nWorkflow Failed: {data.get('error')}")
                break
            
            time.sleep(2)

    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == "__main__":
    test_modular_workflow()

import requests
import json

API_URL = "http://localhost:8000"

def verify_v2():
    print("Verifying v2 Architecture...")
    
    payload = {
        "workflow_id": "KVOORUMI_PHASED_A",
        "initial_inputs": {
            "prompt_text": "Test Prompt",
            "history_text": "Test History",
            "product_text": "Test Product",
            "reflection_text": "Test Reflection"
        }
    }
    
    print(f"1. Calling {API_URL}/run_workflow...")
    try:
        res = requests.post(f"{API_URL}/run_workflow", json=payload)
        
        if res.status_code == 200:
            data = res.json()
            print("   Success! Workflow executed.")
            print("   Final Verdict:", data.get('final_verdict'))
            print("   XAI Report:", data.get('xai_report')[:50] + "...")
            
            # Verify hooks ran
            if 'input_control_ratio' in data:
                print("   [Check] Calculation Hook ran successfully.")
            else:
                print("   [Fail] Calculation Hook did not run.")
                
        else:
            print(f"   Failed: {res.status_code}")
            with open("error_response.txt", "w") as f:
                f.write(res.text)
            print("   Error response saved to error_response.txt")
            
    except Exception as e:
        print(f"   Connection Error: {e}")

if __name__ == "__main__":
    verify_v2()

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def main():
    try:
        # 1. Get List
        r = requests.get(f"{BASE_URL}/executions/recent?limit=6")
        r.raise_for_status()
        recents = r.json()
        
        print(f"Found {len(recents)} executions.")
        
        results = {}

        for exc in recents:
            eid = exc['execution_id']
            # 2. Get Full Status (with hydration)
            r2 = requests.get(f"{BASE_URL}/executions/{eid}")
            if r2.status_code == 200:
                data = r2.json()
                wf_id = data.get('workflow_id')
                status = data.get('status')
                
                print(f"Checking {wf_id} ({status})...")
                
                if status == 'completed':
                    res = data.get('result', {})
                    
                    # Extract Key Indicators
                    score_data = res.get('Report', {}).get('scores', {})
                    raw_steps = res.get('Raw_Steps', {})
                    
                    has_cog_judge = 'step_judge_cognitive' in raw_steps
                    has_std_judge = 'step_judge' in raw_steps
                    
                    results[wf_id] = {
                        "status": status,
                        "scores_present": bool(score_data),
                        "has_cognitive_judge_raw": has_cog_judge,
                        "has_standard_judge_raw": has_std_judge,
                        "verdict": res.get('Report', {}).get('final_verdict')
                    }
                else:
                    results[wf_id] = {"status": status, "error": data.get('error')}
        
        print("\n--- RESULTS SUMMARY ---")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

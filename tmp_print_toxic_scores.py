import json
import sqlite3
import os

db_path = r"c:\src\quorum\data\db_v2.json"

try:
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    # Get the latest execution
    executions = db.get("executions", {})
    if not executions:
        print("No executions found.")
        exit(0)
        
    latest_id = list(executions.keys())[-1]
    latest = executions[latest_id]
    
    print(f"--- RESULTS FOR TOXIC AUDIT ({latest_id}) ---")
    
    results = latest.get("results", {})
    
    evaluative_matrices = [
        "matrix_judge", "matrix_toulmin", "matrix_bloom", 
        "matrix_archivist", "matrix_causal_analyst", "matrix_causal_abductive"
    ]
    
    orthogonal_matrices = [
        "matrix_taskguard", "matrix_falsifier", "matrix_kahneman", 
        "matrix_goodhart", "matrix_taskxai_clarity", "matrix_xai_reporter"
    ]
    
    print("\n--- EVALUATIVE MATRICES (Averaged) ---")
    for step_id, step_data in results.items():
        if isinstance(step_data, dict):
             for k, v in step_data.items():
                 if k in evaluative_matrices:
                     scaled = step_data.get(f"{k}_scaled", "MISSING")
                     normalized = step_data.get(f"{k}_normalized", "MISSING")
                     print(f"  {k}: {v} (Scaled/Clamped: {scaled}, Normalized: {normalized})")
                     
    print("\n--- ORTHOGONAL MATRICES (Penalties/Meta) ---")
    for step_id, step_data in results.items():
        if isinstance(step_data, dict):
             for k, v in step_data.items():
                 if k in orthogonal_matrices:
                     scaled = step_data.get(f"{k}_scaled", "MISSING")
                     normalized = step_data.get(f"{k}_normalized", "MISSING")
                     print(f"  {k}: {v} (Scaled/Clamped: {scaled}, Normalized: {normalized})")

    # Print Scoring Output
    scoring_result = results.get("step_judge", {}).get("scoring_result", {})
    if not scoring_result:
         # Check standard location if different
         for step_id, step_data in results.items():
             if isinstance(step_data, dict) and "scoring_result" in step_data:
                 scoring_result = step_data["scoring_result"]
                 
    print("\n--- FINAL SCORING RESULT ---")
    print(json.dumps(scoring_result, indent=2))

except Exception as e:
    print(f"Error: {e}")

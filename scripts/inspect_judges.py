
import json

path = r"c:\src\quorum\execution_dump.json"
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    step_results = data.get("results", {}).get("step_results", {})
    print("Step Keys:", list(step_results.keys()))
    
    judge_out = step_results.get("step_judge") # Standard Judge
    cog_judge_out = step_results.get("step_judge_cognitive") # Cognitive Judge
    
    if judge_out:
        print("\n--- Standard Judge Found ---")
        print(f"Keys: {list(judge_out.keys())}")
        # Check if it looks like the EvaluationResult model (total_score, dimensions, etc)
        print(f"Total Score: {judge_out.get('pisteet', 'N/A')}") # Likely V1 format in this old run?
        
    if cog_judge_out:
        print("\n--- Cognitive Judge Found ---")
        print(f"Keys: {list(cog_judge_out.keys())}")

except Exception as e:
    print(e)

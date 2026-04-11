import json
import sys

def run():
    try:
        with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        if not executions:
            print("No executions found.")
            return

        last_exec = list(executions.values())[-1]
        data = last_exec.get("data", {})
        
        with open("c:/src/quorum/export_scores_dump.txt", "w", encoding="utf-8") as out:
            out.write(f"Final Score: {last_exec.get('final_score')}\n")
            out.write("\n--- RAW DATA ---\n")
            for k, v in data.items():
                if "_normalized" in k or "_score" in k:
                    out.write(f"{k}: {v}\n")
        print("Scores dumped successfully to export_scores_dump.txt")
    except Exception as e:
        print(f"Error: {e}")

run()

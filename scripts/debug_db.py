import json

def run():
    try:
        db_path = "c:/src/quorum/data/db_v2.json"
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        print("Tietokannan taulut:", list(db.keys()))
        executions = db.get("executions", {})
        print("Ajoja (executions) yhteensä:", len(executions))
        
        for k, ex in executions.items():
            print(f"Key: {k}, ID: {ex.get('id')}, Score: {ex.get('final_score')}")
            
    except Exception as e:
        print(f"Error: {e}")

run()

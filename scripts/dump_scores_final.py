import json

def run():
    try:
        with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        if not executions:
            print("No executions table found in DB.")
            return

        # Nappaa 3 viimeisintä ajoa!
        last_execs = list(executions.values())[-3:]
        
        with open("c:/src/quorum/export_scores_dump.txt", "w", encoding="utf-8") as out:
            for ex in last_execs:
                out.write(f"\n========================================\n")
                out.write(f"Execution ID: {ex.get('id')}\n")
                out.write("\n--- RAW DATA ---\n")
                
                # recursive search for "_normalized", "_score"
                def dump_dict(d, prefix=""):
                    if isinstance(d, dict):
                        for k, v in d.items():
                            if isinstance(v, (dict, list)):
                                dump_dict(v, f"{prefix}{k}.")
                            elif isinstance(k, str) and ("_normalized" in k or "score" in k.lower() or "_is_evaluative" in k):
                                out.write(f"{prefix}{k}: {v}\n")
                    elif isinstance(d, list):
                        for i, v in enumerate(d):
                            dump_dict(v, f"{prefix}[{i}].")
                        
                dump_dict(ex)
                out.write(f"\n========================================\n")
                
        print("Viimeisten kolmen ajon pisteet dumpattu onnistuneesti export_scores_dump.txt!")
    except Exception as e:
        print(f"Error: {e}")

run()

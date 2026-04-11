import json

def run():
    try:
        # Luen sen vanhan poistetun kannan varmuuskopiosta!
        with open("c:/src/quorum/backend_v2/seed/backups/db_v2.json.20260411_144326.bak", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        target_exec = None
        
        # Etsitään kovakoodatulla 58 liukuluvulla tai kääntäen viimeisimmästä
        for ex in list(executions.values())[::-1]:
            score = ex.get("final_score")
            if score == 58.0 or score == 58:
                target_exec = ex
                break

        # Varotoimi: napataan isosta kannasta eka missä on ylipäätään jotain pisteitä
        if not target_exec:
            for ex in list(executions.values())[::-1]:
                if ex.get("final_score") is not None:
                    target_exec = ex
                    break

        if not target_exec:
            print("No execution with a score found even in the massive 5.2MB backup.")
            return

        with open("c:/src/quorum/export_scores_dump.txt", "w", encoding="utf-8") as out:
            out.write(f"Execution ID: {target_exec.get('id')}\n")
            out.write(f"Final Score: {target_exec.get('final_score')}\n")
            out.write("\n--- RAW DATA ---\n")
            
            # recursive search for "_normalized" keys
            def dump_dict(d, prefix=""):
                for k, v in d.items():
                    if isinstance(v, dict):
                        dump_dict(v, prefix)
                    elif isinstance(k, str) and ("_normalized" in k or "_is_evaluative" in k):
                        out.write(f"{k}: {v}\n")
                    
            if "state" in target_exec:
                dump_dict(target_exec.get("state", {}))
            else:
                dump_dict(target_exec)
                
        print("YES! Vanhan 5MB kannan haamupisteet pelastettu export_scores_dump.txt tiedostoon!")
    except Exception as e:
        print(f"Error: {e}")

run()

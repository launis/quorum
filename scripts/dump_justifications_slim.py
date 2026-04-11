import json

def run():
    try:
        # KÄYTETÄÄN SITÄ 5.2 MB BACKUPPIA! Aktiivinen kanta on haamu/keskeneräinen!
        with open("c:/src/quorum/backend_v2/seed/backups/db_v2.json.20260411_144326.bak", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        if not executions:
            return

        last_execs = list(executions.values())[-3:]
        
        with open("c:/src/quorum/justifications_dump.txt", "w", encoding="utf-8") as out:
            out.write("--- LAUSEIDEN TEKSTI-PERUSTELUT (5.2 MB KANNASTA) --- \n\n")
            
            for exec_data in last_execs:
                out.write(f"\n\n========================================\n")
                out.write(f"AJON ID: {exec_data.get('id')}\n")
                out.write(f"========================================\n")
                
                def extract_all_strings(obj, parent_key="root"):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, str) and len(v) > 10:
                                # Suodatetaan koodijutut ja Base64 PDF roskat pois!
                                if len(v) < 3000 and "JVBERi" not in v and "{" not in v and "def " not in v and not v.startswith("ey"):
                                    if not v.startswith("blk_") and not v.startswith("exe_") and not v.startswith("usr_"):
                                        out.write(f"\n[{parent_key}.{k}]\n{v}\n")
                            elif isinstance(v, (dict, list)):
                                extract_all_strings(v, f"{parent_key}.{k}")
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            extract_all_strings(v, f"{parent_key}[{i}]")
                            
                trace = exec_data.get("state", {}).get("execution_trace", [])
                if not trace:
                    trace = exec_data.get("data", {}).get("execution_trace", [])
                
                extract_all_strings(trace, "execution_trace")
                
        print("Tiedosto vihdoin valmis kultasuonelta!")
    except Exception as e:
        print(f"Error: {e}")

run()

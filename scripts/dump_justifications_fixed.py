import json

def run():
    try:
        with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        if not executions:
            return

        last_execs = list(executions.values())[-3:]
        
        with open("c:/src/quorum/justifications_dump.txt", "w", encoding="utf-8") as out:
            out.write("--- KAIKKI PITKÄT TEKSTIT --- \n\n")
            
            for exec_data in last_execs:
                out.write(f"\n\n========================================\n")
                out.write(f"AJON ID: {exec_data.get('id')}\n")
                out.write(f"========================================\n")
                
                # Kuljetaan aggressiivisesti koko pydantic-objekti läpi ilman valitusta
                def extract_all_strings(obj, parent_key="root"):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, str) and len(v) > 60:
                                # Suodatetaan koodijutut pois
                                if "{" not in v and "def " not in v and not v.startswith("ey"):
                                    out.write(f"\n[{parent_key}.{k}]\n{v}\n")
                            elif isinstance(v, (dict, list)):
                                extract_all_strings(v, f"{parent_key}.{k}")
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            extract_all_strings(v, f"{parent_key}[{i}]")
                            
                extract_all_strings(exec_data)
                
        print("Tiedosto päivitetty totaalisella louhinnalla!")
    except Exception as e:
        print(f"Error: {e}")

run()

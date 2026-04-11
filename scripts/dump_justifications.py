import json

def run():
    try:
        with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            
        executions = db.get("executions", {})
        if not executions:
            return

        last_exec = list(executions.values())[-1]
        
        with open("c:/src/quorum/justifications_dump.txt", "w", encoding="utf-8") as out:
            out.write("--- JUSTIFICATIONS FOR MATRIX CLAIMS ---\n\n")
            
            # Recursive search for any dict that looks like it has justifications or claims
            def dump_justifications(d, prefix=""):
                if isinstance(d, dict):
                    # If this dict represents a single claim evaluating to true/false with reasoning
                    if "justification" in d or "reasoning" in d or "is_true" in d:
                        out.write(f"{prefix}:\n")
                        for k, v in d.items():
                            if k in ["statement", "claim", "is_true", "justification", "reasoning", "evidence"]:
                                out.write(f"  {k}: {v}\n")
                        out.write("\n")
                    
                    for k, v in d.items():
                        if isinstance(v, (dict, list)):
                            dump_dict_recursive(v, f"{prefix}.{k}")
            
            def dump_dict_recursive(d, prefix=""):
                if isinstance(d, dict):
                    dump_justifications(d, prefix)
                elif isinstance(d, list):
                    for i, v in enumerate(d):
                        dump_dict_recursive(v, f"{prefix}[{i}]")
                        
            dump_dict_recursive(last_exec)
                
        print("Perustelut viety tiedostoon justifications_dump.txt")
    except Exception as e:
        print(f"Error: {e}")

run()

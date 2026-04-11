import json

def run():
    try:
        filepath = r"c:\src\quorum\data\files\executions\exe_c83d4eb23cef4a4e9aeaa4ea38a1d820\execution_trace.json"
        
        with open(filepath, "r", encoding="utf-8") as f:
            trace = json.load(f)
            
        with open("c:/src/quorum/one_full_justification.md", "w", encoding="utf-8") as out:
            out.write("# 🎭 Kokonainen Perusteluesimerkki (Falsifier / Performativity)\n\n")
            
            # Etsitään yksi rikas arviointiblocki (esim. solmu jossa on tekstiä)
            found = False
            for step in trace:
                content = step.get("content", {})
                if not isinstance(content, dict):
                    continue
                    
                # Etsitään sisältö, jossa on hyvät tekstiperustelut!
                for k, v in content.items():
                    if isinstance(v, dict) and "step_4_final_score" in v and "Say-Do Gap" in v.get("step_4_final_score", ""):
                        # Tulostetaan koko V-objekti nätisti
                        out.write(f"### Kriteerin askeleen ID: `{k}`\n")
                        out.write("Tässä on täsmälleen ne Micro-CoT -askelet The Hookista, jotka johtivat lopulliseen scoreen:\n\n")
                        
                        out.write("```json\n")
                        out.write(json.dumps(v, indent=2, ensure_ascii=False))
                        out.write("\n```\n")
                        
                        found = True
                        break
                
                if found:
                    break
                    
            if not found:
                out.write("Ei löytynyt täydellistä Say-Do Gap -osioita. Kokeillaan ensimmäistä parasta.\n")
                for step in trace:
                    content = step.get("content", {})
                    if not isinstance(content, dict):
                        continue
                    for k, v in content.items():
                        if isinstance(v, dict) and "step_4_final_score" in v:
                            out.write("```json\n")
                            out.write(json.dumps(v, indent=2, ensure_ascii=False))
                            out.write("\n```\n")
                            found = True
                            break
                    if found:
                        break

        print("Dumppaus valmis! Avaa one_full_justification.md.")
    except Exception as e:
        print(f"Error: {e}")

run()

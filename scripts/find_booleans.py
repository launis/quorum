import json

def run():
    try:
        filepath = r"c:\src\quorum\data\files\executions\exe_c83d4eb23cef4a4e9aeaa4ea38a1d820\execution_trace.json"
        
        with open(filepath, "r", encoding="utf-8") as f:
            trace = json.load(f)
            
        print("Tässä ovat kaikki JSON-listan solmut (steps) ja vähän niiden sisältöä:\n")
        
        for i, step in enumerate(trace):
            name = step.get("slug", "unknown_slug")
            
            # Katsotaan onko _normalized täällä
            content = step.get("content", {})
            has_normalized = any(str(k).endswith("_normalized") for k in content.keys())
            has_score_card = "score_card" in content
            
            print(f"[{i}] Solmu: {name}")
            print(f"    - Onko lopulliset pisteytykset (_normalized): {has_normalized}")
            print(f"    - Onko perinteinen score_card: {has_score_card}")
            
            # Etsitään ihan mitä tahansa booleaneja!
            for k, v in content.items():
                if isinstance(v, bool):
                     print(f"    - LÖYTYI SUORA BOOLEAN: {k} = {v}")
                if isinstance(v, list):
                     print(f"    - LÖYTYI LISTA: {k} (Pituus {len(v)})")

        with open("c:/src/quorum/trace_structure.md", "w") as out:
             out.write("Ajon rakenne selvitetty.")
    except Exception as e:
        print(f"Error: {e}")

run()

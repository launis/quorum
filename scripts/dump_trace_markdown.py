import json
import os

def run():
    try:
        # AAAA! Ne ovat tiedostojärjestelmässä (Storage Service)!
        # Luetaan suoraan tuon nimenomaisen huippu-ajon trace-tiedosto!
        target_path = r"c:\src\quorum\data\files\executions\exe_c83d4eb23cef4a4e9aeaa4ea38a1d820\execution_trace.json"
        
        if not os.path.exists(target_path):
            print("Files-kansiota tai tracea ei löytynyt!")
            return
            
        with open(target_path, "r", encoding="utf-8") as f:
            trace = json.load(f)
            
        with open("c:/src/quorum/trace_results_final.md", "w", encoding="utf-8") as out:
            out.write("# 🎭 Zero-Trust Matrix Evaluations (True / False)\n")
            out.write("*Datan lähde: Storage Service Blob (execution_trace.json)*\n\n")
            count = 0
            
            for step in trace:
                content = step.get("content", {})
                if not isinstance(content, dict):
                    continue
                    
                evaluative_findings = []
                for k, v in content.items():
                    # Haetaan kriteerin numeerinen arvosana pydantic-objektin litteästä rakenteesta
                    if isinstance(k, str) and k.endswith("_normalized"):
                        score = v
                        # Parsitaan vastaava teksti jos se löytyy
                        reasoning = ""
                        for r_k, r_v in content.items():
                            if isinstance(r_v, dict) and "step_4_final_score" in r_v:
                                reasoning = r_v.get("step_4_final_score", "")
                                
                        status = "🟢 HYVÄKSYTTY VÄITE" if score > 0 else "🔴 NOLLAPISTE (Sanktiovaatimus)"
                        evaluative_findings.append(f"- **{status}** (Pisteet: {score}):\n  > {reasoning}\n")
                
                if evaluative_findings:
                    out.write(f"### Loogisen Solmun Tuomio\n")
                    for finding in evaluative_findings:
                        out.write(finding)
                    out.write("\n---\n")
                    count += 1
                        
            out.write(f"\n*Löydettiin yhteensä {count} arviointisolmua tiedostosta!*\n")
            
        print("BINGO! Markdown raportti generoitu tiedostosta trace_results_final.md")
    except Exception as e:
        print(f"Error: {e}")

run()

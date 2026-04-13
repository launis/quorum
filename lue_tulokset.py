import json
from pathlib import Path

def print_latest_execution_results():
    db_path = Path(r"C:\src\quorum\data\db_v2.json")
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    executions = db.get("executions", {})
    prompt_blocks = db.get("prompt_blocks", {})
    
    if not executions:
        print("No executions found in db_v2.json")
        return

    latest_exe_key = max(executions.keys(), key=lambda k: int(k) if k.isdigit() else 0)
    latest_exe = executions[latest_exe_key]
    exe_id = latest_exe.get('id', 'N/A')
    
    print("=" * 80)
    print(f" LATEST EXECUTION: {exe_id}")
    print("=" * 80)

    # V2 Arkkitehtuuri tallentaa kaiken raskaamman datan tiedostoon (Forensic Audit Trail)
    trace_path = Path(f"C:\\src\\quorum\\data\\files\\executions\\{exe_id}\\execution_trace.json")
    
    if not trace_path.exists():
        print(f"\n[Virhe] Ei löytynyt execution_trace.json tiedostoa: {trace_path}")
        # Dumppaa varmuuden vuoksi perusavaimet kannasta
        for k, v in latest_exe.get("step_states", {}).items():
            print(f"Step {k}: inputs={list(v.get('inputs', {}).keys()) if isinstance(v.get('inputs'), dict) else 'EI DICT'}, outputs={list(v.get('outputs', {}).keys()) if isinstance(v.get('outputs'), dict) else 'EI DICT'}")
        return

    with open(trace_path, "r", encoding="utf-8") as f:
        trace_data = json.load(f)
        
    print(f"\n✅ LÖYDETTY XAI LOKI! (Koko: {trace_path.stat().st_size / 1024:.1f} KB)\n")

    # Etsi kaikki blk_ alkuiset tulokset trace-blokkien sisältä (yleensä 'outputs' tai 'state_delta' alla)
    found_any = False
    
    # Rekursiivinen etsintä tracesta, jotta löydetään matriisit
    def find_matrices(data, results):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(k, str) and "blk_" in k and isinstance(v, (int, float)):
                    # Osuma!
                    justification = data.get(f"{k}_justification", "Ei perusteluja saatavilla.")
                    missing = data.get(f"{k}_missing_context", "")
                    if missing:
                         justification += f"\n[Puuttuva konteksti]:\n{missing}"
                    results[k] = {"score": v, "just": justification}
                else:
                    find_matrices(v, results)
        elif isinstance(data, list):
            for item in data:
                find_matrices(item, results)

    found_matrices = {}
    find_matrices(trace_data, found_matrices)

    for block_id, data in found_matrices.items():
        found_any = True
        score = data["score"]
        justification = data["just"]
        
        # Etsi suomenkielinen nimi prompt_blocks kokoelmasta
        fi_name = block_id
        for pb_key, pb_meta in prompt_blocks.items():
            if pb_meta.get("id") == block_id or pb_key == block_id:
                label_data = pb_meta.get("label", {})
                translations = label_data.get("translations", {})
                fi_name = translations.get("fi", translations.get("en", pb_meta.get("id_human_readable", block_id)))
                break
        
        print(f"\n🟢 MATRIISI: {fi_name} (ID: {block_id})")
        print(f"   ► PISTEET: {score:.1f}")
        print(f"   ► TEKSTIPLÄJÄYS (XAI Log):")
        for line in justification.split('\n'):
            if line.strip():
                 print(f"       {line}")
        print("-" * 80)

    if not found_any:
        print("Ei löytynyt 'blk_' arvoja trace-tiedostosta. Dumpataan juuriavaimet tracesta:")
        if isinstance(trace_data, dict):
            print(list(trace_data.keys()))
            for k, v in trace_data.items():
                if isinstance(v, list) and len(v) > 0:
                    print(f"- {k} sisältää {len(v)} alkiota. Ensimmäinen alkio:")
                    print("  " + str(v[0])[:200] + "...")
        elif isinstance(trace_data, list):
            print(f"Trace on lista ({len(trace_data)} alkiota).")

if __name__ == "__main__":
    print_latest_execution_results()

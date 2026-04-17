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
                    # Tarkistetaan onko tämä aito matriisi Pydantic-määrittelyistä
                    is_matrix = False
                    
                    # Ohitetaan suoraan kaikki metadatakentät (.endswith)
                    if any(k.endswith(suffix) for suffix in ["_is_evaluative", "_scaled", "_normalized", "_atoms"]):
                        continue

                    # Varmistetaan category_id db_v2.json määritelmistä (joka tuotiin aikaisemmin ulommassa scopessa)
                    for pb_key, pb_meta in prompt_blocks.items():
                        if pb_meta.get("id") == k or pb_key == k:
                            if pb_meta.get("category_id") == "matrix":
                                is_matrix = True
                            break
                    
                    if is_matrix:
                        # Osuma! Oikea arvioitava matriisi
                        justification = data.get(f"{k}_justification", "Ei perusteluja saatavilla.")
                        missing = data.get(f"{k}_missing_context", "")
                        if missing:
                             justification += f"\n[Puuttuva konteksti]:\n{missing}"
                        
                        # Lisätään atomi-laskentalogiikka tulosteeseen, jos ne löytyvät mapista!
                        t_atoms = data.get(f"{k}_total_atoms")
                        t_true = data.get(f"{k}_true_atoms")
                        t_false = data.get(f"{k}_false_atoms")
                        t_levels = data.get(f"{k}_level_breakdown")
                        
                        extra_info = ""
                        level_dict = {}
                        if t_levels:
                            for lvl_key in sorted(t_levels.keys(), key=lambda x: float(x)):
                                lvl_data = t_levels[lvl_key]
                                clean_key = str(int(float(lvl_key))) if float(lvl_key).is_integer() else str(lvl_key)
                                level_dict[clean_key] = f"{lvl_data['hits']}/{lvl_data['total']}"
                        elif t_atoms is not None:
                             extra_info = f"{t_true}/{t_atoms}"
                             
                        results[k] = {"score": v, "just": justification, "extra_info": extra_info, "level_dict": level_dict, "normalized_score": data.get(f"{k}_normalized")}
                else:
                    find_matrices(v, results)
        elif isinstance(data, list):
            for item in data:
                find_matrices(item, results)

    found_matrices = {}
    find_matrices(trace_data, found_matrices)

    eval_lines = []
    other_lines = []
    global_eval_scores = []

    for block_id, data in found_matrices.items():
        found_any = True
        score = data["score"]
        justification = data["just"]
        
        # Etsi suomenkielinen nimi prompt_blocks kokoelmasta
        fi_name = block_id
        scale_max = None
        scale_min = 1.0
        is_evaluative = True # Oletuksena true, jos ei muuta sanota
        
        for pb_key, pb_meta in prompt_blocks.items():
            if pb_meta.get("id") == block_id or pb_key == block_id:
                label_data = pb_meta.get("label", {})
                translations = label_data.get("translations", {})
                fi_name = translations.get("fi", translations.get("en", pb_meta.get("id_human_readable", block_id)))
                is_evaluative = pb_meta.get("is_evaluative", True)
                
                scales = pb_meta.get("scales", [])
                if scales:
                    try:
                        scale_max = max(float(s.get("score", 0)) for s in scales)
                        scale_min = min(float(s.get("score", 0)) for s in scales)
                    except Exception:
                        pass
                break
        
        norm_val = data.get("normalized_score")
        score_str = f"{score:.1f}"
        
        if scale_max is not None:
             if norm_val is not None:
                 score_str = f"{score:.1f}/{float(scale_max):.1f} ({norm_val:.1f}%)"
             else:
                 score_str = f"{score:.1f}/{float(scale_max):.1f}"

        l1 = data.get('level_dict', {}).get("1", "-")
        l2 = data.get('level_dict', {}).get("2", "-")
        l3 = data.get('level_dict', {}).get("3", "-")
        l4 = data.get('level_dict', {}).get("4", "-")
        l5 = data.get('level_dict', {}).get("5", "-")
        
        # JOS extra_info on olemassa (non-level matrix), laitetaan se T1 sarakkeeseen
        if not data.get('level_dict') and data.get('extra_info'):
            l1 = data.get('extra_info')
            
        # Tiivistetään syy ensimmäiseen virkkeeseen
        short_reason = justification.split('\n')[0].strip()
        if '.' in short_reason:
            short_reason = short_reason.split('.')[0] + "."
        if len(short_reason) > 55:
            short_reason = short_reason[:52] + "..."
            
        line_str = f"{fi_name[:32]:<32} | {score_str:<18} | {l1:<10} | {l2:<10} | {l3:<10} | {l4:<10} | {l5:<10} | {short_reason}"
        
        if is_evaluative:
            eval_lines.append(line_str)
            if norm_val is not None:
                global_eval_scores.append(norm_val)
        else:
            other_lines.append(line_str)
            
    # --- TULOSTUS ---
    print(f"\n{'MATRIISI':<32} | {'PIST.':<18} | {'T1':<10} | {'T2':<10} | {'T3':<10} | {'T4':<10} | {'T5':<10} | {'PERUSTELU'}")
    print("=" * 160)
    for line in eval_lines:
        print(line)
        
    print("-" * 160)
    if global_eval_scores:
        avg = sum(global_eval_scores) / len(global_eval_scores)
        print(f"{'► KOKONAISARVOSANA (Keskiarvo)':<36} | {avg:.1f}%")

    if other_lines:
        print("=" * 140)
        print(f"[ INFO-MATRIISIT (Ei vaikutusta keskiarvoon) ]")
        print("-" * 140)
        for line in other_lines:
            print(line)


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

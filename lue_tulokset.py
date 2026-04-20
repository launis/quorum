import json
from pathlib import Path


import sys

def print_latest_execution_results(target_locale: str = "fi"):
    db_path = Path(r"C:\src\quorum\data\db_v2.json")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)

    executions = db.get("executions", {})
    prompt_blocks = db.get("prompt_blocks", {})

    if not executions:
        print("No executions found in db_v2.json")
        return

    latest_exe_key = str(max(executions.keys(), key=lambda k: int(k) if str(k).isdigit() else 0))
    latest_exe = executions[latest_exe_key]
    
    if "id" not in latest_exe:
        raise ValueError("[FAIL-FAST] Opaque Stripe ID 'id' is completely missing from the latest execution dictionary.")
    
    exe_id = latest_exe["id"]

    print("=" * 80)
    print(f" LATEST EXECUTION: {exe_id}")
    print("=" * 80)

    # V2 Arkkitehtuuri tallentaa kaiken raskaamman datan tiedostoon (Forensic Audit Trail)
    trace_path = Path(f"C:\\src\\quorum\\data\\files\\executions\\{exe_id}\\execution_trace.json")

    if not trace_path.exists():
        print(f"\n[Virhe] Ei löytynyt execution_trace.json tiedostoa: {trace_path}")
        # Dumppaa varmuuden vuoksi perusavaimet kannasta
        for k, v in latest_exe.get("step_states", {}).items():
            in_keys = list(v.get('inputs', {}).keys()) if isinstance(v.get('inputs'), dict) else 'EI DICT'
            out_keys = list(v.get('outputs', {}).keys()) if isinstance(v.get('outputs'), dict) else 'EI DICT'
            print(f"Step {k}: inputs={in_keys}, outputs={out_keys}")
        return

    with open(trace_path, encoding="utf-8") as f:
        trace_data = json.load(f)

    print(f"\n✅ LÖYDETTY XAI LOKI! (Koko: {trace_path.stat().st_size / 1024:.1f} KB)\n")

    # Etsi kaikki blk_ alkuiset tulokset trace-blokkien sisältä (yleensä 'outputs' tai 'state_delta' alla)
    found_any = False

    def find_matrices(data, results):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(k, str) and k.startswith("blk_"):
                    # Tarkistetaan onko tämä aito matriisi Pydantic-määrittelyistä
                    is_matrix = False
                    for pb_key, pb_meta in prompt_blocks.items():
                        if pb_meta.get("id") == k or pb_key == k:
                            if pb_meta.get("category_id") == "matrix":
                                is_matrix = True
                            break

                    if is_matrix:
                        # V2 Flat-Schema Mandatory Check (Zero-Fallback Rule)
                        if isinstance(v, dict):
                            # In some architectures (or pre-hook generation), the data is a comprehensive dictionary.
                            score = v.get("step_4_final_score") or v.get("score")
                            if score is not None:
                                justification = v.get("step_1_evidence_quote") or v.get("step_2_falsification") or v.get(f"{k}_justification") or v.get("reasoning")
                                if justification is None:
                                    raise RuntimeError(f"[CRITICAL FAIL FAST] V2 flat-schema metadata missing for '{k}'. No justification found in the output payload.")
                                
                                missing = v.get("extension_missing_context") or v.get("missing_context")
                                just_str = str(justification)
                                if missing:
                                    just_str += f"\n[Puuttuva konteksti]:\n{missing}"

                                level_dict = v.get("level_breakdown", {})
                                norm_score = v.get("normalized_score") or data.get(f"{k}_normalized")
                                extra_info = ""
                                if level_dict and isinstance(level_dict, dict):
                                    clean_level_dict = {}
                                    for lvl_key in sorted(level_dict.keys(), key=lambda x: float(x) if str(x).replace(".", "").isdigit() else 0):
                                        lvl_data = level_dict[lvl_key]
                                        c_key = str(int(float(lvl_key))) if float(lvl_key).is_integer() else str(lvl_key)
                                        clean_level_dict[c_key] = f"{lvl_data.get('hits', 0)}/{lvl_data.get('total', 0)}"
                                    level_dict = clean_level_dict
                                elif v.get("total_atoms") is not None:
                                    extra_info = f"{v.get('true_atoms')}/{v.get('total_atoms')}"

                                existing = results.get(k, {})
                                final_norm = norm_score if norm_score is not None else existing.get("normalized_score")
                                results[k] = {
                                    "score": score, "just": just_str, "extra_info": extra_info,
                                    "level_dict": level_dict, "normalized_score": final_norm
                                }
                            continue

                        if isinstance(v, (int, float)):
                            score = v
                            # Etsi rinnakkaisavaimia (sibling keys)
                            justification = data.get(f"{k}_justification") or data.get(f"{k}_falsification")
                            if not justification:
                                raise RuntimeError(f"[CRITICAL FAIL FAST] V2 flat-schema metadata missing for '{k}'. No justification/falsification found.")

                            t_atoms = data.get(f"{k}_total_atoms")
                            t_true = data.get(f"{k}_true_atoms")
                            t_levels = data.get(f"{k}_level_breakdown")
                            missing = data.get(f"{k}_missing_context") or data.get(f"{k}_missing")
                            norm_score = data.get(f"{k}_normalized") or data.get(f"{k}_normalized_score")

                            just_str = str(justification)
                            if missing:
                                 just_str += f"\n[Puuttuva konteksti]:\n{missing}"

                            extra_info = ""
                            level_dict = {}
                            if t_levels and isinstance(t_levels, dict):
                                for lvl_key in sorted(t_levels.keys(), key=lambda x: float(x)):
                                    lvl_data = t_levels[lvl_key]
                                    clean_key = str(int(float(lvl_key))) if float(lvl_key).is_integer() else str(lvl_key)
                                    level_dict[clean_key] = f"{lvl_data.get('hits', 0)}/{lvl_data.get('total', 0)}"
                            elif t_atoms is not None:
                                 extra_info = f"{t_true}/{t_atoms}"

                            existing = results.get(k, {})
                            final_norm = norm_score if norm_score is not None else existing.get("normalized_score")
                            results[k] = {
                                "score": score, "just": just_str, "extra_info": extra_info,
                                "level_dict": level_dict, "normalized_score": final_norm
                            }

                # Jatka syväetsintää yhä normaaleista litteistä dicta-rakenteista
                if isinstance(v, dict):
                    find_matrices(v, results)
                elif isinstance(v, list):
                    for item in v:
                        find_matrices(item, results)
        elif isinstance(data, list):
            for item in data:
                find_matrices(item, results)

    found_matrices = {}
    find_matrices(trace_data, found_matrices)

    # --- PENALTY SEARCH ---
    found_penalties = {
        "threat_detected": False,
        "post_hoc_rationalization": False
    }

    def find_penalties(data):
        if isinstance(data, dict):
            td = data.get("threat_detected")
            ph = data.get("post_hoc_rationalization")
            if td is True or str(td).lower() == "true":
                found_penalties["threat_detected"] = True
            if ph is True or str(ph).lower() == "true":
                found_penalties["post_hoc_rationalization"] = True

            for v in data.values():
                find_penalties(v)
        elif isinstance(data, list):
            for item in data:
                find_penalties(item)

    find_penalties(trace_data)

    eval_lines = []
    other_lines = []
    global_eval_scores = []

    for block_id, data in found_matrices.items():
        found_any = True
        score = data["score"]
        justification = data["just"]

        # Etsi oikeankielinen nimi prompt_blocks kokoelmasta
        locale_name = block_id
        for pb_key, pb_meta in prompt_blocks.items():
            if pb_meta.get("id") == block_id or pb_key == block_id:
                label_data = pb_meta.get("label", {})
                translations = label_data.get("translations", {})
                locale_name = translations.get(target_locale, translations.get("en", pb_meta.get("id_human_readable", block_id)))
                is_evaluative = pb_meta.get("is_evaluative", True)

                # Hae 'computed_' arvot UI tulostetta varten (PIST.)
                calc_max = pb_meta.get("computed_max")
                
        norm_val = data.get("normalized_score")
        
        scaled_score = float(norm_val) if norm_val is not None else None

        score_str = f"{score:.1f}"
        if calc_max is not None:
             score_str = f"{score:.1f}/{float(calc_max):.1f}"

        l1 = data.get('level_dict', {}).get("1", "-")
        l2 = data.get('level_dict', {}).get("2", "-")
        l3 = data.get('level_dict', {}).get("3", "-")
        l4 = data.get('level_dict', {}).get("4", "-")
        l5 = data.get('level_dict', {}).get("5", "-")
        l6 = data.get('level_dict', {}).get("6", "-")

        # JOS extra_info on olemassa (non-level matrix), laitetaan se T1 sarakkeeseen
        if not data.get('level_dict') and data.get('extra_info'):
            l1 = data.get('extra_info')

        # Tiivistetään syy ensimmäiseen virkkeeseen
        short_reason = justification.split('\n')[0].strip()
        if '.' in short_reason:
            short_reason = short_reason.split('.')[0] + "."
        if len(short_reason) > 42:
            short_reason = short_reason[:39] + "..."

        scaled_str = f"{scaled_score:.1f}%" if scaled_score is not None else "-"
        lvl_str = f"{l1:<7} | {l2:<7} | {l3:<7} | {l4:<7} | {l5:<7} | {l6:<7}"
        line_str = f"{locale_name[:32]:<32} | {score_str:<10} | {lvl_str} | {short_reason:<45} | {scaled_str:<6}"

        if is_evaluative:
            eval_lines.append(line_str)
            if scaled_score is not None:
                global_eval_scores.append(scaled_score)
        else:
            other_lines.append(line_str)

    # --- TULOSTUS ---
    lvl_head = f"{'T1':<7} | {'T2':<7} | {'T3':<7} | {'T4':<7} | {'T5':<7} | {'T6':<7}"
    print(f"\n{'MATRIISI':<32} | {'PIST.':<10} | {lvl_head} | {'PERUSTELU':<45} | {'100%':<6}")
    print("=" * 165)
    for line in eval_lines:
        print(line)

    print("-" * 165)
    if global_eval_scores:
        avg = sum(global_eval_scores) / len(global_eval_scores)
        print(f"{'► KOKONAISARVOSANA (Keskiarvo)':<32} | {'':<10} | {'':<60} | {'':<45} | {avg:.1f}%")

    if other_lines:
        print("=" * 140)
        print("[ INFO-MATRIISIT (Ei vaikutusta keskiarvoon) ]")
        print("-" * 140)
        for line in other_lines:
            print(line)

    # --- PENALTY TULOSTUS ---
    print("=" * 140)
    print("[ RANGAISTUSMEKANISMIT ]")
    print("-" * 140)

    t_flag = "⚠️ AKTIVOITUNUT (Pisteitä alennettu)" if found_penalties["threat_detected"] else "✅ Puhdas"
    print(f" Guard (Turvallisuusuhka):           | {t_flag}")

    p_flag = "⚠️ AKTIVOITUNUT (Pisteitä alennettu)" if found_penalties["post_hoc_rationalization"] else "✅ Puhdas"
    print(f" Falsifier (Jälkikäteisrationalis.): | {p_flag}")
    print("=" * 140)


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
    cli_locale = sys.argv[1] if len(sys.argv) > 1 else "fi"
    print_latest_execution_results(target_locale=cli_locale)

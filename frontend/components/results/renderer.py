import streamlit as st
import pandas as pd

def render_dual_matrix_view(data: dict):
    """
    Renders a comparative view of two Judge matrices dynamically.
    Scans Raw_Steps for any steps containing 'pisteet' and 'judge'/'tuomari' in metadata/key.
    """
    raw = data.get("Raw_Steps", {})
    
    # 1. Dynamic Discovery
    judge_steps = []
    for step_id, step_data in raw.items():
        # Check if it looks like a scored step
        if isinstance(step_data, dict) and "pisteet" in step_data:
            # Check keywords in ID or Agent Name to confirm it's a Judge
            agent_name = step_data.get("metadata", {}).get("agentti", "").lower()
            sid = step_id.lower()
            if "judge" in sid or "tuomari" in sid or "judge" in agent_name or "tuomari" in agent_name:
                judge_steps.append((step_id, step_data))

    if len(judge_steps) != 2:
        st.warning(f"⚠️ Dual Mode active, but found {len(judge_steps)} judge matrices (Expected 2). Showing available raw data.")
        if len(judge_steps) == 1:
             # Fallback to single view for the one found?
             pass
        return

    # 2. Strict Dynamic Identification (No Heuristics)
    # Sort by Step ID to ensure deterministic order (e.g. step_judge comes before step_judge_cognitive)
    judge_steps.sort(key=lambda x: x[0])

    s_left_id, s_left_data = judge_steps[0]
    s_right_id, s_right_data = judge_steps[1]

    # Labels strictly from Metadata
    left_label = s_left_data.get("metadata", {}).get("agentti", s_left_id)
    right_label = s_right_data.get("metadata", {}).get("agentti", s_right_id)

    # Sanity check for identical names
    if left_label == right_label:
        left_label = f"{left_label} ({s_left_id})"
        right_label = f"{right_label} ({s_right_id})"

    pts_l = s_left_data.get("pisteet", {})
    pts_r = s_right_data.get("pisteet", {})
    
    # Common keys
    keys_l = set(pts_l.keys())
    keys_r = set(pts_r.keys())
    common_keys = list(keys_l.intersection(keys_r))
    
    if not common_keys:
         # If no intersection, we can't compare. Just take Left keys to show something.
         common_keys = list(keys_l)

    # Simple alphabetical sort for keys
    common_keys.sort()

    # Header
    cols = st.columns([2, 2, 2, 1, 2])
    cols[0].markdown("**Ulottuvuus**")
    cols[1].markdown(f"**{left_label}**")
    cols[2].markdown(f"**{right_label}**")
    cols[3].markdown("**Delta**")
    cols[4].markdown("**Johtopäätös**")
    st.divider()

    total_l, total_r, count = 0, 0, 0

    def get_val_str(item):
        if isinstance(item, dict): return item.get("arvosana", 0), item.get("perustelu", "")
        return (float(item), "") if isinstance(item, (int, float, str)) and str(item).replace('.','',1).isdigit() else (0, str(item))

    # Helper for formatted score
    def fmt_score_dual(score, s_max=None):
        try:
             s = float(score)
             # integer check
             val_str = f"{s:.0f}" if s.is_integer() else f"{s:.1f}"
             
             if s_max:
                 return f"{val_str}/{s_max}"
             return val_str
        except:
            return str(score)

    for key in common_keys:
        val_l, reason_l = get_val_str(pts_l.get(key))
        val_r, reason_r = get_val_str(pts_r.get(key))
        
        # Get scale max for specific steps
        max_l = s_left_data.get("scale_max")
        max_r = s_right_data.get("scale_max")
        
        try:
             num_l = float(val_l)
             num_r = float(val_r)
        except:
             num_l, num_r = 0, 0

        total_l += num_l
        total_r += num_r
        count += 1
        
        delta = num_r - num_l
        delta_str = f"+{delta:.0f}" if delta > 0 else f"{delta:.0f}"
        if delta == 0: delta_str = "="
        
        # Generic Verdict Logic
        verdict = ""
        if delta > 0:
            verdict = f"📈 {right_label} (+)"
        elif delta < 0:
            verdict = f"📉 {left_label} (+)"
        else:
            verdict = "⚖️ Tasan"
        
        # Color coding delta
        delta_color = "green" if delta > 0 else "red" if delta < 0 else "gray"

        c = st.columns([2, 2, 2, 1, 2])
        c[0].markdown(f"### {key.capitalize()}")
        # Display raw score with scale denominator if available
        c[1].metric(left_label, fmt_score_dual(num_l, max_l), label_visibility="collapsed")
        c[2].metric(right_label, fmt_score_dual(num_r, max_r), label_visibility="collapsed")
        c[3].markdown(f":{delta_color}[**{delta_str}**]")
        c[4].caption(verdict)
        
        with c[0].expander("Perustelut"):
            st.markdown(f"**{left_label}:** {reason_l}")
            st.divider()
            st.markdown(f"**{right_label}:** {reason_r}")
        
        st.divider()

    # Averages
    if count > 0:
        avg_l = round(total_l / count, 1)
        avg_r = round(total_r / count, 1)
        st.markdown(f"**Keskiarvo:** {avg_l} vs. {avg_r}")


def render_dashboard(data: dict):
    """
    Renders the complete audit dashboard based on the result dictionary.
    """
    st.divider()
    st.title("Results Dashboard")

    # 1. High Level Verdict (Report)
    report = data.get("Report", {})
    sys_status = data.get("System_Status", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tuomio (Verdict)", report.get("final_verdict", "N/A"))
    with col2:
        conf = report.get("confidence", 0)
        st.metric("Luottamus", f"{int(conf*100)}%")
    with col3:
        # Example from interaction or calculated
        st.metric("Status", sys_status.get("status", "Completed"))
    with col4:
        st.metric("Risk Level", sys_status.get("riski_taso", "N/A"))

    # 2. Scores
    # 2. Scores (Dual or Single)
    # Check for Dual Mode metadata or infer from steps
    matrix_mode = data.get("matrix_mode") or data.get("_meta", {}).get("matrix_mode")
    
    # Fallback inference if metadata missing
    if not matrix_mode:
        raw = data.get("Raw_Steps", {})
        if "step_judge" in raw and "step_judge_cognitive" in raw:
            matrix_mode = "dual"

    scores = report.get("scores") or report.get("pisteet")
    s_max = report.get("scale_max")

    if matrix_mode == "dual":
        render_dual_matrix_view(data)
        scores = None

    # Helper for formatted score
    def fmt_score(score, s_max=None):
        try:
             s = float(score)
             # integer check
             val_str = f"{s:.0f}" if s.is_integer() else f"{s:.1f}"
             
             if s_max:
                 return f"{val_str}/{s_max}"
             # Heuristic: If > 5, assume it's NOT a small Likert
             return val_str
        except:
            return str(score)

    if scores:
        st.subheader(f"Arviointi (Dynamic Scores)")
        
        # Convert scores dict to list of items for rendering
        score_items = list(scores.items())
        
        # Create rows of 3 columns
        for i in range(0, len(score_items), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(score_items):
                    key, val = score_items[i + j]
                    label = key.replace('_', ' ').capitalize()
                    
                    # Handle value if it's complex (e.g. dict with reasoning) or simple
                    score_val = val
                    selitys = ""
                    
                    # If the flattened report puts explanation in a separate key (e.g. "analyysi_selitys")
                    # we try to find it.
                    possible_selitys_key = f"{key}_selitys"
                    if possible_selitys_key in scores:
                        selitys = scores[possible_selitys_key]
                    
                    # If val is dict (JudgeAgent standard output often has {arvosana: X, perustelu: Y})
                    if isinstance(val, dict):
                        score_val = val.get("arvosana")
                        selitys = val.get("perustelu") or selitys

                    with cols[j]:
                         st.metric(label, fmt_score(score_val, s_max))
                         if selitys:
                             st.caption(selitys)

    # 3. Feedback
    st.subheader("Palaute (Feedback)")
    st.info(report.get("palaute_yhteenveto", "Ei palautetta."))
    
    with st.expander("Toimenpiteet (Valmennusohjeet)", expanded=True):
        # 1. Coaching Actions
        actions = report.get("kehitystoimenpiteet", [])
        if actions:
            st.markdown("**Valmennusohjeet (Coaching):**")
            for act in actions:
                 st.markdown(f"- {act}")
        else:
            st.caption("Ei valmennusohjeita.")

        st.divider()

        # 2. Product Recommendations
        recs = report.get("kehitysehdotukset", [])
        if recs:
            st.markdown("**Suositukset lopputyöhön:**")
            for r in recs:
                st.markdown(f"- {r}")
        else:
             st.caption("Ei lopputyön suosituksia.")

    # 4. Profile & Interaction
    c_prof, c_int = st.columns(2)
    
    with c_prof:
        st.markdown("### 🧠 Psykologinen Profiili")
        # In V2, profile is projected into Report if implemented, or we fallback to Raw Steps
        profile = report.get("psykologinen_profiili", {})
        if not profile:
             # Fallback to Raw Data if Flatten failed to project it
             raw = data.get("Raw_Steps", {})
             if "step_profiler" in raw:
                 profile = raw.get("step_profiler")

        if profile:
            st.write(f"**Profiili:** {profile.get('psykologinen_profiili', profile.get('profiili', 'N/A'))}")
            st.write(f"**Intentio:** {profile.get('intentio_analyysi', profile.get('intentio', 'N/A'))}")
            biases = profile.get("tunnistetut_vinoumat", profile.get("vinoumat", []))
            if biases:
                st.write("**Tunnistetut vinoumat:**")
                for b in biases:
                     # StructuredBias object or string? Flattened State usually keeps Objects inside Raw, but Report might simplify
                     if isinstance(b, dict):
                         st.caption(f"- {b.get('nimi')}: {b.get('selitys')}")
                     else:
                         st.caption(f"- {b}")
        else:
            st.caption("Profiilitieotoja ei saatavilla.")

    with c_int:
        st.markdown("### 📡 Vuorovaikutus")
        interaction = report.get("vuorovaikutus_analyysi", {})
        if not interaction:
             raw = data.get("Raw_Steps", {})
             if "step_interaction" in raw:
                 interaction = raw.get("step_interaction")

        if interaction:
             st.write(f"**Rooli:** {interaction.get('driver_classification', interaction.get('rooli', 'N/A'))}")
             st.write(f"**Kontrollisuhde:** {interaction.get('input_control_ratio', interaction.get('control_ratio', 0))}")
             strats = interaction.get('tunnistetut_strategiat', interaction.get('strategiat', []))
             if strats:
                 st.write("**Strategiat:**")
                 for s in strats:
                     st.caption(f"- {s}")
        else:
             st.caption("Vuorovaikutustietoja ei saatavilla.")

    # 5. Bibliography
    refs = report.get('lahdet', [])
    if refs:
        st.markdown("### 📚 Lähteet (Bibliography)")
        for ref in refs:
            if isinstance(ref, str):
                st.markdown(f"- {ref}")
            else:
                 st.markdown(f"- {ref.get('citation', ref)}")

    # 6. Deep Dive (Evidence & Logic)
    with st.expander("🔍 Syväanalyysi (Todisteet, Logiikka, Faktat)", expanded=False):
        
        # A. XAI Report
        if report.get('xai_report_formatted'):
            st.markdown("#### 📝 XAI Raportti")
            st.markdown(report.get('xai_report_formatted'))
            st.divider()

        # B. Analysis & Hypotheses
        hypos = report.get('analyysi_hypoteesit', [])
        evidence = report.get('analyysi_todisteet', [])
        if hypos or evidence:
            st.markdown("#### 🕵️ Analyysi & Todisteet")
            if hypos:
                st.markdown("**Testatut hypoteesit:**")
                for h in hypos:
                    icon = "✅" if h.get('loytyyko_todisteita') else "❌"
                    st.caption(f"{icon} {h.get('vaite_teksti')}")
            
            if evidence:
                st.markdown("**Löydetyt todisteet (RAG):**")
                for e in evidence:
                    score = e.get('relevanssi_score', 0)
                    st.info(f"({score}%) {e.get('konteksti_segmentti')}")

        # C. Logic
        toulmin = report.get('logiikka_toulmin', [])
        schema = report.get('logiikka_skeema')
        fidelity = report.get('logiikka_uskollisuus')
        if toulmin or schema or fidelity:
            st.markdown("#### 📐 Logiikka & Argumentaatio")
            if schema: st.write(f"**Tunnistettu skeema:** {schema}")
            if fidelity: st.write(f"**Päättelyn uskollisuus:** {fidelity}")
            if toulmin:
                st.markdown("**Toulmin-rakenne:**")
                for t in toulmin:
                    st.text(f"Claim: {t.get('claim')}\nData: {t.get('data')}\nWarrant: {t.get('warrant')}\nBacking: {t.get('backing')}")

        # D. Facts & Ethics
        facts = report.get('faktatarkistus', [])
        ethics = report.get('etiikka', [])
        if facts or ethics:
            st.markdown("#### ⚖️ Faktat & Etiikka")
            for f in facts:
                res = f.get('verifiointi_tulos')
                color = "green" if res == "Vahvistettu" else "red"
                st.markdown(f":{color}[{res}] **{f.get('vaite')}** ({f.get('lahde_tai_paattely')})")
            
            for e in ethics:
                if e.get('tyyppi') != "Ei havaittu":
                    st.warning(f"**{e.get('tyyppi')}** ({e.get('vakavuus')}): {e.get('kuvaus')}")

        # E. Causality & Archivist
        causal = report.get('kausaalisuus_paatelma')
        align = report.get('linjakkuus')
        if causal or align:
            st.markdown("#### 🔗 Kausaalisuus & Linjakkuus")
            if causal: st.write(f"**Kausaalinen päättely:** {causal}")
            if align: st.write(f"**Arkiston linjakkuus:** {align}")

        # F. Pre-Mortem
        pre_mortem = report.get('pre_mortem_analyysi', {})
        if pre_mortem:
            st.markdown("#### 🎭 Performatiivisuus & Pre-Mortem")
            if pre_mortem.get('suoritettu'):
                 st.write(f"**Suoritettu:** Kyllä")
                 signals = pre_mortem.get('hiljaiset_signaalit', [])
                 if signals:
                     st.markdown("**Hiljaiset signaalit:**")
                     for s in signals:
                         st.caption(f"- {s}")
            else:
                 st.caption("Pre-Mortem analyysiä ei suoritettu.")

        # G. Judge Critique
        crit = report.get('kritiikki', [])
        if crit:
            st.markdown("#### 👩‍⚖️ Tuomarin huomiot")
            for c in crit:
                st.caption(f"- {c}")

    # 7. Audit Trail (Technical & Methodological)
    with st.expander("🔬 Audit Trail (Tekninen seuranta & Lokit)", expanded=False):
        raw_steps = data.get("Raw_Steps", {})
        if raw_steps:
             # Sort by step index if possible, or just iterate order
             # Trying to sort by 'vaihe' in metadata
             steps = []
             for key, val in raw_steps.items():
                 meta = val.get('metadata', {})
                 step_num = meta.get('vaihe', 999)
                 if isinstance(step_num, (int, float)):
                     steps.append((step_num, key, val))
                 else:
                     steps.append((999, key, val))
             
             steps.sort(key=lambda x: x[0])
             
             for _, key, step_data in steps:
                 meta = step_data.get('metadata', {})
                 agent = meta.get('agent', key)
                 ver = meta.get('versio', 'N/A')
                 time = meta.get('luontiaika', 'N/A')
                 log = step_data.get('metodologinen_loki')
                 reasoning = step_data.get('reasoning_trace')
                 
                 st.markdown(f"**{agent}** (v{ver}) - *{time}*")
                 
                 # Show Scale if available (Judge Steps)
                 s_min = step_data.get('scale_min')
                 s_max = step_data.get('scale_max')
                 if s_max:
                     st.caption(f"📏 *Scale:* {s_min}-{s_max}")

                 if reasoning:
                     st.caption(f"🧠 *Reasoning:* {reasoning}")
                 if log:
                     st.caption(f"📝 *Log:* {log}")
                 st.divider()

    # 8. Debug / Raw
    with st.expander("Debug Raw Data"):
        st.json(data)

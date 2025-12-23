import streamlit as st

def render_generic_step(key, value, level=1):
    """
    Recursively renders dictionary/list content for dynamic agent displays.
    """
    if isinstance(value, dict):
        if not value: return
        # Display as section
        # If it's a top-level step dict (e.g. step_profiler), use subheader
        if level == 1:
            friendly_name = key.replace("step_", "").replace("_", " ").title()
            st.subheader(f"🧩 {friendly_name}")
            for k, v in value.items():
                render_generic_step(k, v, level + 1)
            st.divider()
        else:
            # Nested dicts
            with st.expander(f"{key.replace('_', ' ').title()}"):
                for k, v in value.items():
                    render_generic_step(k, v, level + 1)
                    
    elif isinstance(value, list):
        if not value: return
        st.markdown(f"**{key.replace('_', ' ').title()}:**")
        for item in value:
            if isinstance(item, (dict, list)):
                 st.json(item) # Fallback for complex nested lists
            else:
                 st.markdown(f"- {item}")
                 
    else:
        # Simple Key-Value
        if value:
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")



def render_dashboard(result):
    st.header("Results")

    # 1. NEW COMPACT VIEW (Report Key)
    if "Report" in result:
        report = result["Report"]
        
        # --- A. VERDICT & SCORES ---
        st.subheader("🏆 Tuomio (Verdict)")
        
        # Top Metrics
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            if report.get("final_verdict"):
                st.markdown(f"### {report['final_verdict']}")
        with c2:
            if report.get("confidence"):
                st.metric("Luottamus", f"{float(report['confidence']):.0%}")
        with c3:
            if report.get("logiikka_uskollisuus"):
                st.metric("Uskollisuus", report['logiikka_uskollisuus'])

        # Scores (0-4)
        if "scores" in report and isinstance(report["scores"], dict):
            s = report["scores"]
            sc1, sc2, sc3 = st.columns(3)
            
            sc1.metric("Analyysi", f"{s.get('analyysi', 0)}/4")
            if s.get('analyysi_selitys'): sc1.caption(s['analyysi_selitys'])
            
            sc2.metric("Arviointi", f"{s.get('arviointi', 0)}/4")
            if s.get('arviointi_selitys'): sc2.caption(s['arviointi_selitys'])
            
            sc3.metric("Synteesi", f"{s.get('synteesi', 0)}/4")
            if s.get('synteesi_selitys'): sc3.caption(s['synteesi_selitys'])

        if report.get("kritiikki"):
            st.markdown("**Kriittiset huomiot:**")
            for crit in report["kritiikki"]:
                st.markdown(f"- {crit}")

        st.divider()

        # --- A2. INTERACTION & PROFILE (NEW structure via Report) ---
        c1, c2 = st.columns(2)
        
        # Interaction Analysis
        ia = report.get("vuorovaikutus_analyysi")
        if ia:
            with c1:
                st.subheader("📡 Vuorovaikutus")
                st.metric("Rooli", ia.get('rooli', 'N/A'))
                st.metric("Kontrollisuhde", f"{ia.get('control_ratio', 0)}%")
                
                if ia.get('strategiat'):
                    st.markdown("**Strategiat:**")
                    for strat in ia['strategiat']:
                        st.caption(f"- {strat}")

        # Psychological Profile
        pp = report.get("psykologinen_profiili")
        if pp:
            with c2:
                st.subheader("🧠 Psykologinen Profiili")
                st.write(f"**Profiili:** {pp.get('profiili')}")
                st.write(f"**Intentio:** {pp.get('intentio')}")
                
                if pp.get('vinoumat'):
                    with st.expander("Tunnistetut Vinoumat"):
                        for bias in pp['vinoumat']:
                            # Handle both dict (Pydantic dump) and string
                            name = bias.get('nimi') if isinstance(bias, dict) else "Vinouma"
                            desc = bias.get('selitys') if isinstance(bias, dict) else str(bias)
                            st.markdown(f"**{name}:** {desc}")

        st.divider()

        # --- B. ANALYSIS DEEP DIVE ---
        st.subheader("🔍 Analyysi (Analysis)")
        
        # Hypotheses
        if report.get("analyysi_hypoteesit"):
            with st.expander("Hypoteesit (Analyst)", expanded=True):
                for h in report["analyysi_hypoteesit"]:
                    icon = "✅" if h.get("loytyyko_todisteita") else "❌"
                    st.write(f"{icon} **{h.get('vaite_teksti')}**")
                    
                    # Match evidence to hypothesis if available
                    # report['analyysi_todisteet'] contains the list
                    if "analyysi_todisteet" in report:
                        evidence_list = [
                            e for e in report['analyysi_todisteet'] 
                            if e.get('viittaa_hypoteesiin_id') == h.get('id')
                        ]
                        if evidence_list:
                            for ev in evidence_list:
                                st.caption(f"↳ *Todiste:* {ev.get('konteksti_segmentti')} ({ev.get('relevanssi_score')}%)")

        # Logic & Argumentation
        toulmin = report.get("logiikka_toulmin")
        schema = report.get("logiikka_skeema")
        if toulmin or schema:
            with st.expander("Logiikka & Argumentaatio", expanded=False):
                if schema:
                    st.info(f"Tunnistettu Skeema: **{schema}**")
                if toulmin:
                    for t in toulmin:
                        st.markdown(f"**Väite:** {t.get('claim')}")
                        st.caption(f"*Peruste:* {t.get('data')} | *Oikeutus:* {t.get('warrant')}")
                        st.markdown("---")

        # Facts & Ethics
        facts = report.get("faktatarkistus")
        ethics = report.get("etiikka")
        
        if facts or ethics:
            c1, c2 = st.columns(2)
            with c1:
                if facts:
                    st.warning("⚠️ Faktantarkistus")
                    for f in facts:
                        st.write(f"- {f.get('vaite')} ({f.get('verifiointi_tulos')})")
            with c2:
                if ethics:
                    st.error("🚫 Eettiset Havainnot")
                    for e in ethics:
                        st.write(f"- {e.get('tyyppi')}: {e.get('kuvaus')}")

        st.divider()

        # --- C. FEEDBACK & COACHING ---
        st.subheader("� Palaute (Feedback)")
        
        if report.get("palaute_yhteenveto"):
            st.success(report["palaute_yhteenveto"])

        actions = report.get("kehitystoimenpiteet")
        if actions:
            st.markdown("**Konkreettiset toimenpiteet:**")
            for action in actions:
                st.markdown(f"- {action}")

        props = report.get("kehitysehdotukset")
        if props:
             with st.expander("Lisää kehitysehdotuksia"):
                 if isinstance(props, list):
                     for p in props:
                         st.markdown(f"- {p}")
                 else:
                     st.write(props)

        if report.get("linjakkuus"):
            st.info(f"Linjakkuus: {report['linjakkuus']}")

        # Sources (Coach 2.0)
        sources = report.get("lahdet")
        if sources:
            st.markdown("### 📚 Lähteet & Viitteet")
            for src in sources:
                st.caption(f"- {src}")

        # Debug Dump Access
                # Debug Dump Access (Raw Data)
        if "Raw_Steps" in result:
             with st.expander("🛠️ Raw Data (Debug)"):
                 st.json(result["Raw_Steps"])
                 
                 import json
                 st.download_button(
                     label="📥 Lataa koko JSON",
                     data=json.dumps(result, indent=2, ensure_ascii=False, default=str),
                     file_name="full_report.json",
                     mime="application/json"
                 )
                 
        return

    # --- FALLBACK: LEGACY RENDERER (Original Code) ---
    # --- End of Render ---
    return

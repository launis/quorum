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

def format_xai_report(data):
    if not data: return None
    # Standardized Report Layout (Finnish Headers)
    md = f"### Tiivistelmä\n{data.get('executive_summary', '')}\n\n"
    
    md += f"**Tuomio:** {data.get('final_verdict', '')}\n"
    md += f"**Luottamus:** {data.get('confidence_score', '')}\n\n"
    
    md += f"### Vahvuudet\n{data.get('analysis_strengths', '')}\n\n"
    md += f"### Heikkoudet\n{data.get('analysis_weaknesses', '')}\n\n"
    md += f"### Mahdollisuudet\n{data.get('analysis_opportunities', '')}\n\n"
    md += f"### Suositukset\n{data.get('analysis_recommendations', '')}\n\n"
    return md

def render_dashboard(result):
    st.header("Results")
    
    # --- System Status Dashboard (Flattened Data) ---
    # Safety & Errors
    uhka = result.get('uhka_havaittu')
    riski = result.get('riski_taso')
    post_hoc = result.get('onko_post_hoc_rationalisointia')
    # Metadata
    timestamp = result.get('luontiaika')
    version = result.get('versio')
    
    if any([uhka is not None, riski, post_hoc is not None]):
        st.subheader("🛡️ Järjestelmän Tila (System Status)")
        m1, m2, m3, m4 = st.columns(4)
        
        # Safety
        if uhka is True:
            m1.error("URHEILU HAVAITTU! (THREAT)")
        elif uhka is False:
            m1.success("Turvallinen (Safe)")
        else:
            m1.info("Turvallisuus: N/A")
            
        # Risk Level
        if riski:
            m2.metric("Riski Taso", riski)
            
        # Falsifier
        if post_hoc is True:
            m3.error("Post-Hoc Rationalisointi!")
        elif post_hoc is False:
            m3.success("Logiikka: Valid")
            
        # Metadata
        if timestamp:
            m4.caption(f"Luotu: {timestamp}")
            if version:
                m4.caption(f"Versio: {version}")
        
        st.divider()

        st.divider()

    # --- Profiler Agent ---
    prof_data = result.get('step_profiler') or {}
    # Flattened fallback
    if not prof_data and result.get('psykologinen_profiili'):
        prof_data = result

    if prof_data:
        p_profile = prof_data.get('psykologinen_profiili')
        p_biases = prof_data.get('tunnistetut_vinoumat')
        p_manip = prof_data.get('manipulaatio_yritykset')
        
        if any([p_profile, p_biases, p_manip]):
            st.subheader("🧠 Profiloija (Profiler)")
            c1, c2 = st.columns(2)
            
            with c1:
                if p_profile:
                    st.markdown("**Psykologinen Profiili:**")
                    st.info(p_profile)
                if p_manip:
                    st.markdown("**Manipulaatioyritykset:**")
                    st.warning(p_manip) if p_manip != "Ei havaittu selkeää manipulaatiota." else st.success(p_manip)

            with c2:
                if p_biases:
                    st.markdown("**Tunnistetut Vinoumat:**")
                    if isinstance(p_biases, list):
                        for b in p_biases:
                            if isinstance(b, dict):
                                # New Structure: {nimi, selitys}
                                name = b.get('nimi', 'Tuntematon')
                                desc = b.get('selitys', '')
                                with st.expander(f"⚠️ {name}"):
                                    st.write(desc)
                            else:
                                # Legacy: String
                                st.write(f"- {b}")
                    else:
                        st.write(p_biases)
            st.divider()

    # --- Archivist Agent ---
    arch_data = result.get('step_archivist') or {}
    # Flattened fallback
    if not arch_data and result.get('linjakkuus_analyysi'):
        arch_data = result
        
    if arch_data:
        a_linja = arch_data.get('linjakkuus_analyysi')
        a_suositus = arch_data.get('suositus_tuomarille')
        a_cases = arch_data.get('viitatut_ennakkotapaukset')
        
        if any([a_linja, a_suositus, a_cases]):
            st.subheader("📚 Arkistonhoitaja (Archivist)")
            
            if a_suositus:
                st.markdown(f"**Suositus Tuomarille:** {a_suositus}")
            
            c1, c2 = st.columns(2)
            with c1:
                if a_linja:
                    st.markdown("**Linjakkuusanalyysi:**")
                    st.write(a_linja)
            with c2:
                if a_cases:
                    st.markdown("**Viitatut Ennakkotapaukset:**")
                    if isinstance(a_cases, list):
                         for case in a_cases:
                             st.caption(f"📄 {case}")
                    else:
                         st.caption(a_cases)
            st.divider()

    # --- Judge Scores ---
    score_analyysi = result.get('analyysi') or result.get('step_judge', {}).get('pisteet', {}).get('analyysi')
    score_arviointi = result.get('arviointi') or result.get('step_judge', {}).get('pisteet', {}).get('arviointi')
    score_synteesi = result.get('synteesi') or result.get('step_judge', {}).get('pisteet', {}).get('synteesi')

    if score_analyysi or score_arviointi:
        st.subheader("🏆 Pisteytys (BARS 1-4)")
        s_col1, s_col2, s_col3 = st.columns(3)
        
        def show_score(col, title, s_data):
            if s_data:
                col.metric(label=title, value=f"{s_data.get('arvosana')}/4")
                col.caption(s_data.get('perustelu', ''))

        show_score(s_col1, "Analyysi", score_analyysi)
        show_score(s_col2, "Arviointi", score_arviointi)
        show_score(s_col3, "Synteesi", score_synteesi)
        st.divider()

    # --- XAI Report ---
    report_data = None
    if result.get('analysis_strengths') or result.get('executive_summary'):
         report_data = result
    elif result.get('step_reporter'):
         report_data = result.get('step_reporter')

    if report_data:
        report_md = format_xai_report(report_data)
        st.subheader("📝 XAI Report")
        st.markdown(report_md)
    else:
        # Try fallbacks
        report_md = (
            result.get('xai_report_formatted') or 
            result.get('xai_report_content') or 
            result.get('product_text') 
        )
        if report_md:
             st.subheader("📝 Output Text")
             st.markdown(report_md)
        else:
             st.warning("Report content not found.")

    # --- Coach Report ---
    # --- Coach Report ---
    coach_data = result.get('step_coach')
    # Fallback for flattened data
    if not coach_data and (result.get('kannustava_palaute') or result.get('kehityskohteet_konkreettisesti')):
        coach_data = result
        
    if coach_data:
        st.subheader("🏋️ Valmentajan Palaute (Coach)")
        
        # 1. Kannustava palaute
        if coach_data.get('kannustava_palaute'):
            st.info(coach_data['kannustava_palaute'], icon="🌟")
            
        # 2. Oppimispolku
        if coach_data.get('oppimispolku_viikko'):
            st.markdown("#### 📅 Viikon Oppimispolku")
            st.info(coach_data['oppimispolku_viikko'])

        # 3. Kehityskohteet (Konkreettiset) + Resurssit
        items = coach_data.get('kehityskohteet_konkreettisesti')
        if items:
            st.markdown("#### 🚀 Kehityskohteet")
            for i, item in enumerate(items):
                # Handle distinct formats (dict vs obj)
                otsikko = item.get('otsikko', 'Kohde')
                kuvaus = item.get('kuvaus', '')
                resurssit = item.get('resurssit', [])
                
                with st.expander(f"{i+1}. {otsikko}", expanded=True):
                    st.write(kuvaus)
                    if resurssit:
                        st.caption("📚 Lähteet & Teoria:")
                        for res in resurssit:
                            st.markdown(f"- {res}")

        # 4. Lopputuloksen kehitysehdotukset
        dev_props = coach_data.get('lopputuloksen_kehitysehdotukset')
        if dev_props:
             st.markdown("#### 📝 Lopputuloksen Parannusehdotukset")
             if isinstance(dev_props, list):
                for item in dev_props:
                    st.markdown(f"- {item}")
             else:
                st.write(dev_props)
        
        st.divider()

    # --- Generic Agent Rendering ---
    st.divider()
    st.markdown("### 🧩 Agent Details")
    
    # Sort keys to ensure some order
    all_keys = [k for k in result.keys() if k.startswith("step_")]
    special_steps = ['step_reporter', 'step_judge', 'step_coach'] # Rendered separately
    
    for key in all_keys:
        if key not in special_steps:
            render_generic_step(key, result[key])

    # Raw JSON
    with st.expander("View Raw Output JSON"):
        st.json(result)

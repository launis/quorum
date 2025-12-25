import streamlit as st
import time
import os
import json
import pandas as pd
from frontend.api import APIClient
from frontend.components import render_dashboard

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
api_client = APIClient(BACKEND_URL)

def get_workflow_map():
    """Helper to fetch workflows and return id->dict map for consistent UI."""
    try:
        wfs = api_client.get_workflows()
        return {w['id']: w for w in wfs} if wfs else {}
    except: return {}

st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")
st.title("Cognitive Quorum v2 - Dynamic Workflow Engine")
st.markdown(f"**Backend:** `{BACKEND_URL}`")

# Sidebar: Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Assessment", "Workflow Builder", "Admin", "System Info"])

if page == "Assessment":
    # Sidebar: Workflow Selection
    st.sidebar.header("Configuration")
    selected_workflow_id = None
    
    workflow_options = get_workflow_map()
    if workflow_options:
        selected_workflow_id = st.sidebar.selectbox(
            "Valitse Työnkulku (Select Workflow)",
            options=list(workflow_options.keys()),
            format_func=lambda x: workflow_options[x].get('name', x),
            key="ui_selected_workflow_id"
        )
        if selected_workflow_id:
            st.sidebar.subheader("Model Mapping")
            wf = workflow_options[selected_workflow_id]
            mapping = wf.get('default_model_mapping', {})
            if mapping:
                # Sort mapping by execution order
                execution_order = wf.get('steps', [])
                # Create a list of (step_id, model_name) tuples sorted by index in execution_order
                # If a step is in mapping but not in execution steps (unlikely), put it at the end.
                
                def get_sort_key(item):
                    step_id, _ = item
                    try:
                        return execution_order.index(step_id)
                    except ValueError:
                        return 9999
                
                sorted_mapping = sorted(mapping.items(), key=get_sort_key)

                for step, model in sorted_mapping:
                    if model in ["fast", "deep"]:
                        st.sidebar.markdown(f"**{step}**: `{model}` (Global Strategy)")
                    else:
                        st.sidebar.markdown(f"**{step}**: `{model}`")
            else:
                st.sidebar.caption("No custom model mapping.")
    else:
        st.sidebar.warning("No workflows found or backend unreachable.")
        workflow_options = {}

    # Main Area: Inputs
    st.header("1. Syötä Todistusaineisto (Evidence)")
    
    # --- Auto-Resume Logic ---
    # Convert 'active_job_id' to persistent check if not in session
    if 'active_job_id' not in st.session_state:
        # Check if we have a running job in backend
        try:
            recents = api_client.get_recent_runs(limit=1)
            if recents:
                last_run = recents[0]
                status = last_run.get('status', '').lower()
                # If running or pending, auto-attach explicitly
                if status in ['running', 'pending']:
                    st.session_state['active_job_id'] = last_run['execution_id']
                    st.toast(f"Resumed monitoring active job: {last_run['execution_id']}")
                    time.sleep(0.5) 
                    st.rerun()
                # If failed/rejected recently (e.g. < 5 mins), maybe show notification?
                # For now just let history handle it, users might want to start new one.
        except Exception:
            pass

    col1, col2 = st.columns(2)
    with col1:
        history_file = st.file_uploader("Keskusteluhistoria (Chat Logs)", type=['txt', 'pdf', 'docx'])
    with col2:
        product_file = st.file_uploader("Lopputuote (Final Product)", type=['txt', 'pdf', 'docx'])
        reflection_file = st.file_uploader("Itsearviointi (Reflection)", type=['txt', 'pdf', 'docx'])
    
    # Buttons
    b_col1, b_col2 = st.columns([1, 1])
    start_clicked = False
    
    with b_col1:
        if st.button("Käynnistä Arviointi (Run Assessment)"):
            start_clicked = True
            
    with b_col2:
        # Resume functionality logic
        if 'active_job_id' in st.session_state:
             st.info(f"Active Job: {st.session_state['active_job_id']}")
             if st.button("Clear Active Job"):
                 del st.session_state['active_job_id']
                 st.rerun()

    # --- Job Tracking Logic (Robust) ---
    job_id = st.session_state.get('active_job_id')

    # Start Button Logic
    if start_clicked:
        if not selected_workflow_id:
             st.error("Please select a workflow.")
        elif not history_file or not product_file or not reflection_file:
             st.error("Please upload all 3 files.")
        else:
             with st.spinner("Starting Workflow..."):
                 try:
                     files = {}
                     inputs_metadata = {} 
                     if history_file: files["history_text"] = (history_file.name, history_file.getvalue())
                     if product_file: files["product_text"] = (product_file.name, product_file.getvalue())
                     if reflection_file: files["reflection_text"] = (reflection_file.name, reflection_file.getvalue())
                     
                     job_data = api_client.start_execution(selected_workflow_id, files, inputs_metadata)
                     job_id = job_data['execution_id']
                     st.session_state['active_job_id'] = job_id
                     st.success(f"Job Started! ID: {job_id}")
                     st.rerun() # Rerun to enter the tracking loop below
                 except Exception as e:
                     st.error(f"Client Error: {e}")

    # Polling / Tracking Loop (Checks session_state job_id)
    if job_id:
        st.divider()
        st.subheader(f"Execution Status: {job_id}")
        
        dynamic_steps_order = []
        # Try to guess steps from selected workflow if possible, otherwise we might just default
        if selected_workflow_id:
             dynamic_steps_order = api_client.get_workflow_steps(selected_workflow_id, workflow_options)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_container = st.container()
        
        # We need a loop that keeps running while status is ACTIVE
        # But we also need to render buttons if FAILED.
        
        while True:
             status_data = api_client.get_execution_status(job_id)
             if not status_data:
                 time.sleep(2)
                 continue
                 
             status = status_data.get('status')
             
             # Calculate Progress
             current_step = status_data.get('current_step')
             pct = status_data.get('progress')

             if pct is not None:
                 # Use backend-reported percent
                 progress_bar.progress(min(pct / 100.0, 1.0))
                 if current_step:
                     status_text.info(f"{current_step}")
                 else:
                     status_text.info(f"Status: {status} ({pct}%)")
             
             elif current_step and dynamic_steps_order and current_step in dynamic_steps_order:
                  idx = dynamic_steps_order.index(current_step)
                  progress = (idx + 1) / len(dynamic_steps_order)
                  progress_bar.progress(min(progress, 0.95))
                  status_text.info(f"Vaihe {idx+1}/{len(dynamic_steps_order)}: {current_step} käynnissä...")
             else:
                  # Fallback / Start
                  progress_bar.progress(0.1) 
                  if current_step:
                       status_text.info(f"{current_step}")
                  else:
                       status_text.info(f"Status: {status} ...")

             # Handle Terminal States
             if status and status.upper() == "COMPLETED":
                 progress_bar.progress(100)
                 status_text.success("Assessment Completed!")
                 result = status_data.get('result', {})
                 with result_container:
                      render_dashboard(result)
                 # Allow clearing
                 if st.button("Start New Assessment"):
                      del st.session_state['active_job_id']
                      st.rerun()
                 break
             
             elif status and status.upper() == "FAILED":
                 status_text.error(f"Job Failed: {status_data.get('error')}")
                 
                 col_retry, col_clear = st.columns(2)
                 with col_retry:
                      if st.button("🔄 Retry / Resume (From last success)"):
                           try:
                               import requests
                               res = requests.post(f"{BACKEND_URL}/workflows/executions/{job_id}/retry")
                               if res.status_code == 200:
                                    st.success("Resuming...")
                                    time.sleep(1)
                                    st.rerun()
                               else:
                                    st.error(f"Retry failed: {res.text}")
                           except Exception as e:
                               st.error(f"Retry Error: {e}")
                 with col_clear:
                      if st.button("Cancel & Clear"):
                           del st.session_state['active_job_id']
                           st.rerun()
                 break
             
             elif status and status.upper() == "REJECTED":
                 status_text.error(f"⚠️ Security Intervention (Rejected): {status_data.get('error')}")
                 if 'result' in status_data:
                      with st.expander("Details"):
                          st.json(status_data['result'])
                 if st.button("Acknowledge & Clear"):
                      del st.session_state['active_job_id']
                      st.rerun()
                 break
             
             # If still running
             time.sleep(2)
             # Streamlit reruns logic: we are in a loop.
             # If we want to allow UI interaction (like stop), we rely on Streamlit's "Stop" button or browser refresh.
             # But st.button inside loop won't work well.
             # However, since we are BLOCKING here, the user can't click things easily unless they break the loop.
             # Actually, Streamlit recommends st.empty() and just sleeping. 
             # But if we want responsiveness we rely on st.rerun() interval?
             # For now, this blocking loop is fine for "Watching".
             
             # To allow breaking out manually, we can check for a stop button outside? No.
             pass

    # History Section
    st.subheader("Historia")
    with st.expander("Selaa aiempia ajoja", expanded=False):
        if st.button("Hae viimeiset 5 ajoa"):
            runs = api_client.get_recent_runs()
            if runs:
                st.session_state['recent_runs'] = runs
            else:
                st.warning("Ei ajoja löytynyt tai yhteysvirhe.")

        if 'recent_runs' in st.session_state and st.session_state['recent_runs']:
            runs = st.session_state['recent_runs']
            run_options = {f"{r.get('start_time', 'N/A')} - {r.get('status')} ({r.get('execution_id')[:8]}...)": r for r in runs}
            selected_label = st.selectbox("Valitse ajo:", options=list(run_options.keys()))
            
            if st.button("Lataa valittu tulos"):
                selected_run = run_options[selected_label]
                if selected_run.get('status') == 'completed':
                    if 'result' in selected_run:
                        st.success(f"Ladattu ajo: {selected_run.get('execution_id')}")
                        render_dashboard(selected_run['result'])
                    else:
                        st.warning("Valitussa ajossa ei ole tulosta.")
                else:
                    st.warning(f"Valittu ajo on tilassa: {selected_run.get('status')}")
                    st.json(selected_run)

elif page == "Admin":
    st.header("Admin / Tooling")
    
    tabs = st.tabs(["Knowledge Base", "Agent Registry", "Concept Extractor", "Citation Lookup", "Maintenance"])
    
    # --- Tab 1: Knowledge Base Ingestion ---
    with tabs[0]:
        st.subheader("Knowledge Base Ingestion")
        st.markdown("Upload a DOCX file (e.g., `Holistinen Mestaruus.docx`) to ingest it into the Knowledge Base.")
        
        uploaded_kb = st.file_uploader("Upload Knowledge Base File", type=['docx'])
        
        if uploaded_kb:
            if st.button("Ingest Knowledge Base File"):
                with st.spinner("Ingesting file..."):
                    try:
                        import requests
                        files = {"file": (uploaded_kb.name, uploaded_kb.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                        res = requests.post(f"{BACKEND_URL}/admin/knowledge-base/upload", files=files)
                        
                        if res.status_code == 200:
                            data = res.json()
                            job_id = data.get("job_id")
                            st.success(f"Ingestion Started! Job ID: {job_id}")
                            
                            # Polling Loop
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            while True:
                                try:
                                    status_res = requests.get(f"{BACKEND_URL}/admin/knowledge-base/status/{job_id}")
                                    if status_res.status_code == 200:
                                        status = status_res.json()
                                        percent = status.get("percent", 0)
                                        stage = status.get("stage", "Processing...")
                                        state = status.get("status", "unknown")
                                        
                                        progress_bar.progress(percent)
                                        status_text.info(f"{state.upper()}: {stage}")
                                        
                                        if state in ["completed", "failed"]:
                                            if state == "completed":
                                                st.success("Ingestion Completed Successfully!")
                                                st.json(status.get("result"))
                                            else:
                                                st.error(f"Ingestion Failed: {status.get('error')}")
                                            break
                                    else:
                                        status_text.warning("Waiting for status...")
                                        
                                    time.sleep(1)
                                except Exception as e:
                                    st.error(f"Polling error: {e}")
                                    break
                        else:
                            st.error(f"Ingestion Failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- Tab 2: Agent Registry ---
    with tabs[1]:
        st.subheader("Agent Registry")
        st.write("---")
        # Workflow Context Selector (Identical Logic)
        selected_wf_id = None
        wf_map = get_workflow_map()
        if wf_map:
             # Sync logic
             def_idx = 0
             if "ui_selected_workflow_id" in st.session_state and st.session_state["ui_selected_workflow_id"] in wf_map:
                 def_idx = list(wf_map.keys()).index(st.session_state["ui_selected_workflow_id"])
             
             # Using same label as Sidebar for consistency
             selected_wf_id = st.selectbox(
                 "Valitse Työnkulku (Select Workflow)", 
                 options=list(wf_map.keys()),
                 index=def_idx,
                 format_func=lambda x: wf_map[x].get('name', x),
                 key="registry_wf_selector"
             )

        try:
            import requests
            res = requests.get(f"{BACKEND_URL}/agents", params={"workflow_id": selected_wf_id} if selected_wf_id else None)
            if res.status_code == 200:
                agents = res.json()
                if agents:
                    # Convert to minimal DataFrame for overview
                    df_data = []
                    for a in agents:
                         df_data.append({
                             "Name": a.get("name"),
                             "Model": a.get("model"),
                             "Description": a.get("description", "").split("\n")[0] # First line only
                         })
                    st.dataframe(pd.DataFrame(df_data))
                    
                    # Detailed View
                    st.divider()
                    st.markdown("### Agent Details")
                    sel_agent = st.selectbox("View Schema for Agent:", [a['name'] for a in agents])
                    if sel_agent:
                        agent_data = next((a for a in agents if a['name'] == sel_agent), None)
                        if agent_data:
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("**Output Schema (Response Structure)**")
                                schema_out = agent_data.get('output_schema')
                                if schema_out:
                                    st.json(schema_out)
                                else:
                                    st.caption("No output schema defined.")
                                
                                schema_in = agent_data.get('input_schema')
                                if schema_in:
                                     st.markdown("**Input Schema**")
                                     st.json(schema_in)
                            
                            with c2:
                                st.markdown("**Full Description**")
                                st.markdown(agent_data.get('description'))
                else:
                    st.info("No agents registered yet.")
            else:
                st.error(f"Failed to fetch agents: {res.status_code}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    # --- Tab 3: Concept Extractor ---
    with tabs[2]:
        st.subheader("LLM Concept Extractor")
        st.markdown("Test the concept extraction logic without saving to DB.")
        
        ex_text = st.text_area("Paste Text to Extract Concepts From:", height=200)
        
        if st.button("Extract Concepts"):
             if not ex_text:
                 st.warning("Please enter text.")
             else:
                 with st.spinner("Analyzing text with LLM..."):
                     try:
                         import requests
                         # Use tool endpoint
                         res = requests.post(f"{BACKEND_URL}/tools/extract-concepts", json=ex_text) # Body as string? Router expects Body(embed=False) or check definition
                         # Router: text: str = Body(None) -> Requires JSON body "text" or raw string? 
                         # Actually my router def: text: str = Body(None). If content-type json, expects match.
                         # Better to use requests.post(..., json=payload) with payload={"text": ex_text} if model, or just data=ex_text ?
                         # FastApi Body(embed=False) usually takes raw body if media_type matches.
                         # Let's check router: text: str = Body(None) implies JSON body key "text" if embed=False default? No, usually body param name implies key unless embed=False.
                         # Actually simpler: Use multipart/form-data with "text" field, compatible with the UploadFile logic in the same endpoint.
                         
                         form_data = {"text": ex_text}
                         res = requests.post(f"{BACKEND_URL}/tools/extract-concepts", data=form_data)
                         
                         if res.status_code == 200:
                             result = res.json()
                             concepts = result.get("concepts", [])
                             st.success(f"Found {len(concepts)} concepts!")
                             st.json(concepts)
                         else:
                             st.error(f"Error: {res.text}")
                     except Exception as e:
                         st.error(f"Request failed: {e}")

    # --- Tab 4: Citation Lookup ---
    with tabs[3]:
        st.subheader("Citation Lookup")
        st.markdown("Check if text contains citations known to the Knowledge Base (Coach Logic).")
        
        cit_text = st.text_area("Paste Text to Check:", height=200)
        if st.button("Check Citations"):
             with st.spinner("Checking..."):
                 try:
                     import requests
                     # Router: text: str = Body(..., embed=True) -> Expects JSON {"text": "..."}
                     res = requests.post(f"{BACKEND_URL}/tools/citation-lookup", json={"text": cit_text})
                     
                     if res.status_code == 200:
                         data = res.json()
                         citations = data.get("citations", [])
                         if citations:
                             st.success(f"Found {len(citations)} citations!")
                             for c in citations:
                                 st.markdown(f"- {c}")
                         else:
                             st.info("No citations found.")
                     else:
                         st.error(f"Error: {res.text}")
                 except Exception as e:
                     st.error(f"Failed: {e}")

    # --- Tab 5: Maintenance ---
    with tabs[4]:
        st.subheader("System Maintenance")
        if st.button("Run Self-Test"):
            try:
                import requests
                res = requests.post(f"{BACKEND_URL}/admin/self-test")
                st.json(res.json())
            except Exception as e:
                st.error(e)

elif page == "Workflow Builder":
    from frontend.pages.workflow_builder import render_workflow_builder
    render_workflow_builder(api_client)

elif page == "System Info":
    st.header("System Configuration & Seed Data")
    
    data = api_client.get_seed_data()
    if data:
        # Unified Master View
        st.subheader("📚 Komponenttikirjasto")
        unified_text = api_client.get_unified_prompts()
        if unified_text:
            st.text_area("Unified Content", unified_text, height=800)
            st.download_button("Download Unified View", unified_text, file_name="unified_system_view.md")
        
        st.markdown("---")
        
        # Components
        st.subheader("1. Components (Prompts)")
        all_components = data.get('components', [])
        relevant_types = ['prompt', 'Mandate', 'Rule', 'instruction', 'header', 'protocol', 'method', 'task']
        components = [c for c in all_components if c.get('type') in relevant_types]
        
        if components:
            for i, comp in enumerate(components):
                with st.expander(f"{comp.get('id')} ({comp.get('type')})"):
                    st.text_area("Content", comp.get('content'), height=300, key=f"comp_{comp.get('id')}_{i}")
        
        # Steps
        st.subheader("2. Steps")
        steps = data.get('steps', [])
        if steps:
            st.dataframe(pd.DataFrame(steps))

        # Workflows
        st.subheader("3. Workflows")
        st.json(data.get('workflows', []))
        
        # Preview
        st.subheader("4. Prompt Preview")
        if steps:
            step_ids = [s['id'] for s in steps]
            selected_step = st.selectbox("Select Step to Preview", step_ids)
            if selected_step:
                preview_data = api_client.get_prompt_preview(selected_step)
                if preview_data:
                    st.markdown(f"**Agent Class:** `{preview_data.get('agent_class')}`")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### System Instruction")
                        st.text_area("System", preview_data.get('system_instruction'), height=500)
                    with c2:
                        st.markdown("### User Prompt")
                        st.text_area("User", preview_data.get('user_prompt'), height=500)

        # Full Chain
        st.subheader("🎬 Unified Master View (Execution Chain)")
        workflows = data.get('workflows', [])
        if workflows:
            wf_ids = [w['id'] for w in workflows]
            sel_wf = st.selectbox("Select Workflow for Full Chain", wf_ids, key="full_chain_wf")
            if st.button("Generate Full Chain Preview"):
                full_text = api_client.get_full_chain_preview(sel_wf)
                if full_text:
                    st.text_area("Full Chain Prompt", full_text, height=800)
                    st.download_button("Download", full_text, file_name=f"full_chain_{sel_wf}.txt")
    else:
        st.error("Failed to load seed data.")

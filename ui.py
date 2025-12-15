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

st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")
st.title("Cognitive Quorum v2 - Dynamic Workflow Engine")
st.markdown(f"**Backend:** `{BACKEND_URL}`")

# Sidebar: Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Assessment", "System Info"])

if page == "Assessment":
    # Sidebar: Workflow Selection
    st.sidebar.header("Configuration")
    selected_workflow_id = None
    
    workflows = api_client.get_workflows()
    if workflows:
        workflow_options = {wf['id']: wf for wf in workflows}
        selected_workflow_id = st.sidebar.selectbox(
            "Select Workflow",
            options=list(workflow_options.keys())
        )
        if selected_workflow_id:
            st.sidebar.subheader("Model Mapping")
            wf = workflow_options[selected_workflow_id]
            st.sidebar.json(wf.get('default_model_mapping', {}))
    else:
        st.sidebar.warning("No workflows found or backend unreachable.")
        workflow_options = {}

    # Main Area: Inputs
    st.header("1. Syötä Todistusaineisto (Evidence)")
    
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
        # Resume functionality logic: Fetch last run and display?
        # The original code just set a flag. Let's make it fetch recent runs.
        pass

    if start_clicked:
        if not selected_workflow_id:
            st.error("Please select a workflow.")
        elif not history_file or not product_file or not reflection_file:
            st.error("Please upload all 3 files.")
        else:
            with st.spinner("Starting Workflow..."):
                try:
                    # Prepare Multipart Payload
                    files = {}
                    inputs_metadata = {} 

                    if history_file:
                        files["history_text"] = (history_file.name, history_file.getvalue())
                    if product_file:
                        files["product_text"] = (product_file.name, product_file.getvalue())
                    if reflection_file:
                        files["reflection_text"] = (reflection_file.name, reflection_file.getvalue())
                    
                    job_data = api_client.start_execution(selected_workflow_id, files, inputs_metadata)
                    job_id = job_data['execution_id']
                    st.success(f"Job Started! ID: {job_id}")
                    
                    # --- Polling Loop ---
                    # Get Steps for progress bar
                    dynamic_steps_order = api_client.get_workflow_steps(selected_workflow_id, workflow_options)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        status_data = api_client.get_execution_status(job_id)
                        if not status_data:
                            time.sleep(2)
                            continue
                            
                        status = status_data.get('status')
                        
                        if status and status.upper() == "COMPLETED":
                            progress_bar.progress(100)
                            status_text.success("Assessment Completed!")
                            result = status_data.get('result', {})
                            render_dashboard(result)
                            break
                        
                        elif status and status.upper() == "FAILED":
                            status_text.error(f"Job Failed: {status_data.get('error')}")
                            break
                        
                        elif status and status.upper() == "REJECTED":
                            status_text.error(f"⚠️ Security Intervention (Rejected): {status_data.get('error')}")
                            # Optional: Render partial result if available
                            if 'result' in status_data:
                                with st.expander("Details"):
                                    st.json(status_data['result'])
                            break
                        
                        else:
                            current_step = status_data.get('current_step')
                            if current_step and current_step in dynamic_steps_order:
                                idx = dynamic_steps_order.index(current_step)
                                progress = (idx + 1) / len(dynamic_steps_order)
                                progress_bar.progress(min(progress, 0.95))
                                status_text.info(f"Vaihe {idx+1}/{len(dynamic_steps_order)}: {current_step} käynnissä...")
                            elif current_step:
                                status_text.info(f"Status: {status} - Processing: {current_step}")
                            else:
                                status_text.info(f"Status: {status}...")
                                
                            time.sleep(2)
                            
                except Exception as e:
                    st.error(f"Client Error: {e}")

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

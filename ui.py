import streamlit as st
import requests
import time
import os
import json
import pandas as pd

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
    try:
        # Fetch workflows from API
        response = requests.get(f"{BACKEND_URL}/db/workflows")
        if response.status_code == 200:
            workflows = response.json()
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
            st.sidebar.error(f"Failed to fetch workflows: {response.status_code}")
    
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")

    # Main Area: Inputs
    st.header("1. Syötä Todistusaineisto (Evidence)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        history_file = st.file_uploader("Keskusteluhistoria (Chat Logs)", type=['txt', 'pdf', 'docx'])
    
    with col2:
        product_file = st.file_uploader("Lopputuote (Final Product)", type=['txt', 'pdf', 'docx'])
        reflection_file = st.file_uploader("Itsearviointi (Reflection)", type=['txt', 'pdf', 'docx'])
    
    if st.button("Käynnistä Arviointi (Run Assessment)"):
        if not selected_workflow_id:
            st.error("Please select a workflow.")
        elif not history_file or not product_file or not reflection_file:
            st.error("Please upload all 3 files.")
        else:
            with st.spinner("Starting Workflow..."):
                try:
                    # Prepare files for upload
                    files = {
                        "history_file": (history_file.name, history_file, history_file.type),
                        "product_file": (product_file.name, product_file, product_file.type),
                        "reflection_file": (reflection_file.name, reflection_file, reflection_file.type)
                    }
                    
                    # Start Job
                    response = requests.post(
                        f"{BACKEND_URL}/orchestrator/run",
                        params={"workflow_id": selected_workflow_id},
                        files=files
                    )
                    
                    if response.status_code == 200:
                        job_data = response.json()
                        job_id = job_data['execution_id']
                        st.success(f"Job Started! ID: {job_id}")
                        
                        # Polling Loop
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        while True:
                            try:
                                status_res = requests.get(f"{BACKEND_URL}/orchestrator/status/{job_id}")
                                if status_res.status_code == 200:
                                    status_data = status_res.json()
                                    status = status_data.get('status')
                                    
                                    if status and status.upper() == "COMPLETED":
                                        progress_bar.progress(100)
                                        status_text.success("Assessment Completed!")
                                        result = status_data.get('result', {})
                                        
                                        st.header("2. Results")
                                        
                                        # Helper to format XAI Report
                                        def format_xai_report(data):
                                            if not data: return None
                                            md = f"# {data.get('executive_summary', 'XAI Report')}\n\n"
                                            md += f"**Verdict:** {data.get('final_verdict')}\n"
                                            md += f"**Confidence:** {data.get('confidence_score')}\n\n"
                                            
                                            for section in data.get('detailed_analysis', []):
                                                md += f"## {section.get('title')}\n"
                                                md += f"{section.get('content')}\n\n"
                                                if section.get('visualizations'):
                                                    md += "**Visualizations:**\n"
                                                    for v in section.get('visualizations'):
                                                        md += f"- {v}\n"
                                                md += "\n"
                                            return md

                                        # Display XAI Report
                                        # Check for hoisted fields first (New V2 format)
                                        if result.get('final_verdict') and result.get('detailed_analysis'):
                                            report_data = result
                                        else:
                                            # Fallback to nested format
                                            report_data = result.get('step_9_reporter')

                                        if report_data:
                                            report_md = format_xai_report(report_data)
                                        else:
                                            report_md = (
                                                result.get('xai_report_formatted') or 
                                                result.get('xai_report_content') or 
                                                result.get('xai_report') or 
                                                result.get('report_content') or
                                                result.get('product_text') or
                                                result.get('safe_data', {}).get('product_text') or
                                                result.get('1_tainted_data.json', {}).get('product_text')
                                            )
                                        
                                        # Explicitly display scores if available
                                        if result.get('step_8_judge'):
                                            scores = result['step_8_judge'].get('pisteet', {})
                                            if scores:
                                                st.subheader("🏆 Pisteytys (BARS 1-4)")
                                                s_col1, s_col2, s_col3 = st.columns(3)
                                                
                                                def show_score(col, title, s_data):
                                                    if s_data:
                                                        col.metric(label=title, value=f"{s_data.get('arvosana')}/4")
                                                        col.caption(s_data.get('perustelu')[:150] + "...")

                                                show_score(s_col1, "Analyysi", scores.get('analyysi_ja_prosessi'))
                                                show_score(s_col2, "Arviointi", scores.get('arviointi_ja_argumentaatio'))
                                                show_score(s_col3, "Synteesi", scores.get('synteesi_ja_luovuus'))
                                                st.divider()
                                        
                                        if report_md:
                                            st.subheader("📝 XAI Report (or Product Text)")
                                            st.markdown(report_md)
                                        else:
                                            st.warning("Report content not found in result.")
                                        with st.expander("View Raw Output JSON"):
                                            st.json(result)
                                        break
                                    
                                    elif status and status.upper() == "FAILED":
                                        status_text.error(f"Job Failed: {status_data.get('error')}")
                                        break
                                    
                                    else:
                                        current_step = status_data.get('current_step')
                                        if current_step:
                                            status_text.info(f"Status: {status} - Processing: {current_step}")
                                        else:
                                            status_text.info(f"Status: {status}...")
                                        time.sleep(2)
                                else:
                                    st.warning(f"Failed to poll status (Code: {status_res.status_code}). Retrying...")
                                    time.sleep(2)
                            except requests.exceptions.ConnectionError:
                                st.warning("Connection lost. Retrying...")
                                time.sleep(2)
                            except Exception as e:
                                st.error(f"Polling Error: {e}")
                                break
                    else:
                        st.error(f"Failed to start job: {response.text}")
    
                except Exception as e:
                    st.error(f"Client Error: {e}")

elif page == "System Info":
    st.header("System Configuration & Seed Data")
    
    try:
        response = requests.get(f"{BACKEND_URL}/db/seed_data")
        if response.status_code == 200:
            data = response.json()
            
            # Unified Master View (Printable)
            st.subheader("Unified Master View (Printable)")
            
            try:
                unified_res = requests.get(f"{BACKEND_URL}/config/unified-prompts")
                if unified_res.status_code == 200:
                    unified_text = unified_res.json().get("content", "")
                    st.text_area("Unified Content (with Schemas)", unified_text, height=800)
                    st.download_button("Download Unified View", unified_text, file_name="unified_system_view.md")
                else:
                    st.error(f"Failed to fetch unified prompts: {unified_res.text}")
            except Exception as e:
                st.error(f"Error fetching unified prompts: {e}")
            
            st.markdown("---")

            # Display Components (Prompts)
            st.subheader("1. Components (Prompts)")
            all_components = data.get('components', [])
            # Filter prompt, Mandate, and Rule components
            relevant_types = ['prompt', 'Mandate', 'Rule', 'instruction', 'header', 'protocol', 'method', 'task']
            components = [c for c in all_components if c.get('type') in relevant_types]
            
            if components:
                for i, comp in enumerate(components):
                    with st.expander(f"{comp.get('id')} ({comp.get('type')})"):
                        st.text_area("Content", comp.get('content'), height=300, key=f"comp_{comp.get('id')}_{i}")
            else:
                st.info("No components found.")

            # Display Steps
            st.subheader("2. Steps")
            steps = data.get('steps', [])
            if steps:
                # Convert to DataFrame for better display, selecting key columns
                df_steps = pd.DataFrame(steps)
                st.dataframe(df_steps)
            else:
                st.info("No steps found.")

            # Display Workflows
            st.subheader("3. Workflows")
            workflows = data.get('workflows', [])
            if workflows:
                st.json(workflows)
            else:
                st.info("No workflows found.")
                
            # Prompt Preview
            st.subheader("4. Prompt Preview")
            steps = data.get('steps', [])
            if steps:
                step_ids = [s['id'] for s in steps]
                selected_step = st.selectbox("Select Step to Preview", step_ids)
                
                # Auto-fetch preview when step is selected
                if selected_step:
                    try:
                        preview_res = requests.get(f"{BACKEND_URL}/db/preview_prompt/{selected_step}")
                        if preview_res.status_code == 200:
                            preview_data = preview_res.json()
                            
                            st.markdown(f"**Agent Class:** `{preview_data.get('agent_class')}`")
                            
                            col_p1, col_p2 = st.columns(2)
                            
                            with col_p1:
                                st.markdown("### System Instruction")
                                st.text_area("System Instruction", preview_data.get('system_instruction'), height=500)
                                
                            with col_p2:
                                st.markdown("### User Prompt (Template)")
                                st.text_area("User Prompt", preview_data.get('user_prompt'), height=500)
                        else:
                            st.error(f"Failed to fetch preview: {preview_res.text}")
                    except Exception as e:
                        st.error(f"Error fetching preview: {e}")
            
            # Full Chain Preview
            st.subheader("5. Full Chain Preview")
            workflows = data.get('workflows', [])
            if workflows:
                wf_ids = [w['id'] for w in workflows]
                selected_wf = st.selectbox("Select Workflow for Full Chain", wf_ids, key="full_chain_wf")
                
                if st.button("Generate Full Chain Preview"):
                    try:
                        res = requests.get(f"{BACKEND_URL}/db/preview_full_chain/{selected_wf}")
                        if res.status_code == 200:
                            full_text = res.json().get("full_chain_text", "")
                            st.text_area("Full Chain Prompt", full_text, height=800)
                            st.download_button("Download Full Chain Prompt", full_text, file_name=f"full_chain_{selected_wf}.txt")
                        else:
                            st.error(f"Failed to fetch full chain: {res.text}")
                    except Exception as e:
                        st.error(f"Error fetching full chain: {e}")
            else:
                st.info("No workflows found for full chain preview.")

        else:
            st.error(f"Failed to load seed data. Status: {response.status_code}, Error: {response.text}")
            
    except Exception as e:
        st.error(f"Error fetching seed data: {e}")




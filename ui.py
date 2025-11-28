import streamlit as st
import requests
import time
import os
import json

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")

st.title("Cognitive Quorum v2 - Dynamic Workflow Engine")
st.markdown(f"**Backend:** `{BACKEND_URL}`")

# Sidebar: Workflow Selection
st.sidebar.header("Configuration")
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
        selected_workflow_id = None

except Exception as e:
    st.sidebar.error(f"Connection Error: {e}")
    selected_workflow_id = None

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
                    job_id = job_data['job_id']
                    st.success(f"Job Started! ID: {job_id}")
                    
                    # Polling Loop
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        status_res = requests.get(f"{BACKEND_URL}/orchestrator/status/{job_id}")
                        if status_res.status_code == 200:
                            status_data = status_res.json()
                            status = status_data.get('status')
                            
                            if status == "COMPLETED":
                                progress_bar.progress(100)
                                status_text.success("Assessment Completed!")
                                result = status_data.get('result', {})
                                
                                st.header("2. Results")
                                
                                # Display XAI Report
                                report_md = result.get('xai_report') or result.get('report_content')
                                if report_md:
                                    st.subheader("📝 XAI Report")
                                    st.markdown(report_md)
                                else:
                                    st.warning("Report content not found in result.")
                                
                                # Raw JSON
                                with st.expander("View Raw Output JSON"):
                                    st.json(result)
                                break
                            
                            elif status == "FAILED":
                                status_text.error(f"Job Failed: {status_data.get('error')}")
                                break
                            
                            else:
                                status_text.info(f"Status: {status}...")
                                time.sleep(2)
                        else:
                            st.error("Failed to poll status.")
                            break
                else:
                    st.error(f"Failed to start job: {response.text}")

            except Exception as e:
                st.error(f"Client Error: {e}")

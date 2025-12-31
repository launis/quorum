import streamlit as st
import time

def render_controls(api_client, selected_workflow_id, uploaded_files):
    """
    Renders the Start/Stop controls and handles job submission.
    """
    b_col1, b_col2 = st.columns([1, 1])
    
    with b_col1:
        # Role Check
        user = st.session_state.get('user')
        role = user['role'].lower() if user else 'viewer'

        if role == 'viewer':
            st.warning("⚠️ Viewers have Read-Only access.")
        elif st.button("Käynnistä Arviointi (Run Assessment)"):
            if not selected_workflow_id:
                st.error("Please select a workflow.")
                return
            
            # Validation: Expect 3 files
            # Note: uploaded_files is a dict with keys like 'history_text'
            required_keys = ['history_text', 'product_text', 'reflection_text']
            missing = [k for k in required_keys if k not in uploaded_files]
            
            if missing:
                st.error(f"Please upload all 3 files. Missing: {missing}")
                return
            
            with st.spinner("Starting Workflow..."):
                try:
                    inputs_metadata = {} 
                    token = st.session_state.get('auth_token')
                    job_data = api_client.start_execution(selected_workflow_id, uploaded_files, inputs_metadata, token=token)
                    job_id = job_data['execution_id']
                    st.session_state['active_job_id'] = job_id
                    st.success(f"Job Started! ID: {job_id}")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Client Error: {e}")

    with b_col2:
        if 'active_job_id' in st.session_state:
             st.info(f"Active Job: {st.session_state['active_job_id']}")
             if st.button("Clear Active Job"):
                 del st.session_state['active_job_id']
                 st.rerun()

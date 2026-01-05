
import streamlit as st


def init_session_state():
    """Initializes global session state variables if they don't exist.

    Ensures that key keys like 'active_job_id', 'recent_runs', and UI keys are present
    in Streamlit's session state to prevent KeyErrors.
    """
    if 'active_job_id' not in st.session_state:
        # Default to None, logic elsewhere will check backend if needed
        pass

    if 'recent_runs' not in st.session_state:
        st.session_state['recent_runs'] = []

    # UI State variables
    if 'ui_selected_workflow_id' not in st.session_state:
        st.session_state['ui_selected_workflow_id'] = None

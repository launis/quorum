import streamlit as st
import os
import sys

# Add project root to path to allow absolute imports (e.g. from frontend.utils...)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Utils
from frontend.utils.session_manager import init_session_state
from frontend.api import APIClient

# Views
from frontend.views.audit_view import render_audit_view
from frontend.views.admin_view import render_admin_view
from frontend.views.system_view import render_system_view
from frontend.views.builder_view import render_workflow_builder
from frontend.views.config_view import render_config_view # New View
from frontend.views.matrix_view import render_matrix_view # New View

# Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
api_client = APIClient(BACKEND_URL)

def get_workflow_map():
    try:
        wfs = api_client.get_workflows()
        return {w['id']: w for w in wfs} if wfs else {}
    except: return {}

def main():
    st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")
    
    # Init State
    init_session_state()
    
    st.title("Cognitive Quorum v2 - Dynamic Workflow Engine")
    st.markdown(f"**Backend:** `{BACKEND_URL}`")

    # Sidebar
    with st.sidebar:
        st.title("🧠 Cognitive Quorum")
        st.caption("v2.1 Modular Monolith")
        st.divider()
        
        st.markdown("### Navigation")
        page = st.radio("Go to", ["Assessment", "Workflow Builder", "Global Config", "Audit Matrix Library", "Admin", "System Info"], label_visibility="collapsed")
        
        st.divider()
        st.caption(f"Backend: `{BACKEND_URL}`")
        if "session_id" in st.session_state:
            st.caption(f"Session: `{st.session_state['session_id'][:8]}...`")
    
    # Fetch Data
    workflow_options = get_workflow_map()

    # Routing
    if page == "Assessment":
        render_audit_view(api_client, BACKEND_URL, workflow_options)
        
    elif page == "Workflow Builder":
        render_workflow_builder(api_client)

    elif page == "Global Config":
        render_config_view(api_client, BACKEND_URL)

    elif page == "Audit Matrix Library":
        render_matrix_view(api_client, BACKEND_URL)
        
    elif page == "Admin":
        render_admin_view(api_client, BACKEND_URL, workflow_options)
        
    elif page == "System Info":
        render_system_view(api_client)

if __name__ == "__main__":
    main()
